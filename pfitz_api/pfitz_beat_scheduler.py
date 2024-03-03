from django_celery_beat.schedulers import DatabaseScheduler
from decouple import config
import pika
import ssl

import logging

logger = logging.getLogger(__name__)

class PfitzRabbitMQLockedScheduler(DatabaseScheduler):

    ## this option is set when running multiple servers in an autoscaling group
    multi_instance = config("CELERY_BEAT_MULTI_INSTANCE", cast=bool, default=False)

    def initLockConnection(self):

        try:
            logger.debug("Connecting to rabbitMQ")
            # SSL Context for TLS configuration of Amazon MQ for RabbitMQ

            # set up a connection to rabbitmq using pika
            if config("PIKA_SCHEME") == "SSL":
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')
                url = "amqps://{user}:{password}@{host}:5671".format(user=config("PIKA_USR"), password=config("PIKA_PWD"), host=config("PIKA_HOST"))
                parameters = pika.URLParameters(url)
                parameters.ssl_options = pika.SSLOptions(context=ssl_context)
            else:
                url = "amqp://{user}:{password}@{host}:5672".format(user=config("PIKA_USR"), password=config("PIKA_PWD"), host=config("PIKA_HOST"))
                parameters = pika.URLParameters(url)

            self.lock_connection = pika.BlockingConnection(parameters)
            return True
        except Exception as error:
            logger.debug('Failed to connect to RabbitMQ: %s', str(error))
            self.lock_connection = None
            self.lock_channel = None
            return False
        

    def initLockQueue(self):
        try:
            # set up an exclusive queue in radditmq
            logger.debug("Declaring exclusive lock")

            # check if we have an open channel
            if not hasattr(self, 'lock_channel'):
                logger.debug("Preparing channel")
                self.lock_channel = self.lock_connection.channel()
            elif self.lock_channel.is_closed:
                logger.debug("Reopening closed channel")
                # open a channel if we do not have one
                self.lock_channel = self.lock_connection.channel()

            # if channel established then declarethe exclusive queue
            self.lock_channel.queue_declare(queue=self.lock_queue_name, exclusive=True)

            return True
        except Exception as error:
            logger.debug('Failed to declare exclusive queue: %s', str(error))
            return False
        
    def doesLockQueueExist(self):
        try:
            # declare the queue, this will fail if another instance already has the queue
            logger.debug("Check if lock is exists")
            self.lock_channel.queue_declare(queue=self.lock_queue_name, passive=True)
            return True
        except Exception as error:
            # if the broker closes the channel, the queue doesn't exist
            logger.debug('Lock queue doesnt exist: %s', str(error))
            return False
            
    def hasLock(self):
        try:
            # Declare the queue, this will fail if another instance already has the queue
            logger.debug("Check if lock is owned by this instance")
            self.lock_channel.queue_declare(queue=self.lock_queue_name, passive=True)
            return True
        except Exception as error:
            # If the broker closes the channel, the queue doesn't exist
            logger.debug('Lock queue doesnt exist: %s', str(error))
            
            return False


    def tick(self, *args, **kwargs):

        if PfitzRabbitMQLockedScheduler.multi_instance:
            # when we are running a multi server deployment

            if not hasattr(self, 'lock_tick_counter'):
                # these attributes allow us to increase interval between ticks and preserve compute resources
                self.lock_tick_counter = 0
                self.lock_check_tick_interval = config("PFITZ_SCHEDULER_LOCK_CHECK_INTERVAL", cast=int, default=5)
                self.can_tick = False
            elif self.lock_tick_counter < self.lock_check_tick_interval:
                self.lock_tick_counter += 1
            else:
                # when counter overflows then its time to tick.
                self.lock_tick_counter = 0

                # check if channel and connection exist and create them if not exists
                if not hasattr(self, 'lock_connection'):
                    self.lock_queue_name = 'pfitz-celerybeat-lock'
                    if self.initLockConnection():
                        self.initLockQueue()

                else:
                    self.initLockQueue()

                # check if this instance has the lock
                if self.hasLock():
                    logger.debug("Lock obtained, can now tick")
                    self.can_tick = True
                else:
                    logger.debug("Lock unavailable, stop ticking")
                    self.can_tick = False

            # run tick if lock established
            if self.can_tick:
                logger.debug("MULTI SCHEDULER TICKING")
                super().tick(*args, **kwargs)
        
        else:
            # in single server instance deployment just go ahead and tick
            logger.debug("SINGLE SCHEDULER TICKING")
            super().tick(*args, **kwargs)
    
    # clean up the mess
    def __del__(self):
        try:
            logger.debug("Closing a connection")
            if hasattr(self, 'lock_connection'):
                self.lock_connection.close()
        except Exception as error:
            logger.error("Could not close connection: %s", str(error))

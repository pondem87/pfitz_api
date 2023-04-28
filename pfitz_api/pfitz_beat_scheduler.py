from django_celery_beat.schedulers import DatabaseScheduler
from decouple import config
import pika

import logging

logger = logging.getLogger(__name__)

class PfitzRabbitMQLockedScheduler(DatabaseScheduler):

    def initLockConnection(self):

        try:
            logger.debug("Connecting to rabbitMQ")
            self.lock_connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=config("PIKA_HOST"),
                port=config("PIKA_PORT"),
                credentials=pika.PlainCredentials(username=config("PIKA_USR"), password=config("PIKA_PWD"))))
            return True
        except Exception as error:
            logger.error('Failed to connect to RabbitMQ: %s', str(error))
            self.lock_connection = None
            self.lock_channel = None
            return False
        

    def initLockQueue(self):
        try:
            logger.debug("Declaring exclusive lock")
            if not hasattr(self, 'lock_channel'):
                logger.debug("Preparing channel")
                self.lock_channel = self.lock_connection.channel()
            elif self.lock_channel.is_closed:
                logger.debug("Reopening closed channel")
                self.lock_channel = self.lock_connection.channel()
            self.lock_channel.queue_declare(queue=self.lock_queue_name, exclusive=True)
            return True
        except Exception as error:
            logger.error('Failed to declare exclusive queue: %s', str(error))
            return False
        
    def doesLockQueueExist(self):
        try:
            # Declare the queue
            logger.debug("Check if lock is exists")
            self.lock_channel.queue_declare(queue=self.lock_queue_name, passive=True)
            return True
        except Exception as error:
            # If the broker closes the channel, the queue doesn't exist
            logger.error('Lock queue doesnt exist: %s', str(error))
            
            return False
            
    def hasLock(self):
        try:
            # Declare the queue
            logger.debug("Check if lock is owned by this instance")
            self.lock_channel.queue_declare(queue=self.lock_queue_name, passive=True)
            return True
        except Exception as error:
            # If the broker closes the channel, the queue doesn't exist
            logger.error('Lock queue doesnt exist: %s', str(error))
            
            return False


    def tick(self, *args, **kwargs):

        if not hasattr(self, 'lock_tick_counter'):
            self.lock_tick_counter = 0
            self.lock_check_tick_interval = config("PFITZ_SCHEDULER_LOCK_CHECK_INTERVAL", cast=int, default=5)
            self.can_tick = False
        elif self.lock_tick_counter < self.lock_check_tick_interval:
            self.lock_tick_counter += 1
        else:
            self.lock_tick_counter = 0

            if not hasattr(self, 'lock_connection'):
                self.lock_queue_name = 'pfitz-celerybeat-lock'
                if self.initLockConnection():
                    self.initLockQueue()

            else:
                self.initLockQueue()

            if self.hasLock():
                logger.debug("Lock obtained, can now tick")
                self.can_tick = True
            else:
                logger.debug("Lock unavailable, stop ticking")
                self.can_tick = False


        if self.can_tick:
            logger.debug("SCHEDULER TICKING")
            super().tick(*args, **kwargs)
        
    
    def __del__(self):
        try:
            logger.debug("Closing a connection")
            if hasattr(self, 'lock_connection'):
                self.lock_connection.close()
        except Exception as error:
            logger.error("Could not close connection: %s", str(error))

## ZIMGPT

### Description
This is the backend component of a web based application for interacting with open ai's chat gpt.
It is particularly targetted at the Zimbabwean population where open ai's own website did not provide service.
It provides 2 interfaces to interact with chat gpt. The first is a web application written in React Js using Next Js framework. The second is a whatsapp based chat bot.
The webhook for interacting with whatsapp is implemented through the whatsapp app of the django project.
The interaction with the AI is in two forms. The first is in chat form with conversation memory. The second is meant for scholar type question where an essay form answer is preferred with no conversation memory.
Users are required to create an account and then purchase tokens using a mobile money wallet from Zimbabwe. This can be done either through whatsapp or via the web application.
The web application and whatsapp chatbot allow realtime purchase of tokens.

## Implementation
This is the backend for the next-js and whatsapp app ZimGPT
It interacts with a postgres database which stores all the user information, interacts with the open ai server as well as whatsapp endpoints.
Celery is used to queue up tasks with rabbitmq and subsequently process the task asynchronously and send back a response.

### Celery and RabbitMQ
This is used in two use cases.
First use case is when handling whatsapp webhook. When whatsapp posts a request to our webhook, we parse the payload and figure out the requested service. We send back a 200 response immediately and create a celery task and put it on the queue. The task will then be run when there is available celery worker and a response sent to the user via whatsapp.
Second use case is when web users request a long response such as an essay. A websocket connection is established using django channels and rabbitMQ, and a celery task is created that will eventually open a streaming connection with the upstream server. whenever the task receives a server event, it forwards the response to the client through the open websocket connection. This allows the user to receive part of the answer as soon as it is available and improves user experience.

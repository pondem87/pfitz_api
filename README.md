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
This is the backend for the next-js and whatsapp app ZimGPT and uses the Django framework.
Makes use of daphne, celery, rabbitmq and postgres database.

### PostgreSQL
The app interacts with a postgres database which stores all the user information and scheduling information for celery.

### Celery, RabbitMQ and daphne
This is used in two use cases.First use case is when handling whatsapp webhook. When whatsapp posts a request to our webhook, we parse the payload and figure out the requested service. We send back a 200 response immediately and create a celery task and put it on the queue. The task will then be run when there is available celery worker and a response sent to the user via whatsapp.

Second use case is when web users request a long response. A websocket connection is established using django channels and rabbitMQ, and a celery task is created that will eventually open a streaming connection with the upstream server. whenever the task receives a server event, it forwards the response to the client through the open websocket connection. This allows the user to receive part of the answer as soon as it is available and improves user experience.

Daphne is used for Django channels and rabbitmq is used for the channel layer. RabbitMQ also helps with task queue for celery.

### Whatsapp business
Whats app is used as a second interface for the client. The whatsapp app implements a webhook url that receives and parses the payload from whatsapp server. A custom state machine is implemented in Django to manage converstion with the client as well as allow payments to be made via mobile money wallet using an interactive process with chat messages.

### Celery beat scheduler
Due to limitations of the "Paynow" service for mobile money wallet services in Zimbabwe we had to comme up with a schedule to check for payment status updates. After making a payment, the Paynow server is supposed to post status updates to our return URL, however, this did not happen as specified in Paynow's documentation. This meant our server had to poll Paynow server for status updates. We wanted our payment url request to return a response to the client as soon as the upstream request was sent and not continue polling for any amount of time before returning a response to our client. This meant that somehow at some arbitrary point in the future our server would need to follow up on all pending payments and update their statuses. Our solution was to create an entry in the task scheduler for each payment, which would make make requests to paynow server at regular intervals up to a specified period and then the task is deleted from the database. Firstly the task would expire, and then a regular clean up task would delete all expired tasks at specified intervals. This means the user will be automatially alerted via whatsapp when a payment status changes and service would automatically resume.

The beat scheduler was customised to add a lock implemented using rabbitmq locked queue. This was done to avoid duplication of tasks in a setup where multiple servers where running celery-beat while sharing a single database. It was necessary to ensure that only one server can run the tick method. Each server tried to declare an exclusive queue and only proceeds with the tick if sucessful.

## Django apps

### Dashboard
The dashboard provides an easy interface for admins.
It uses the inbuilt django templates to create a dashboard using html, css with bootstrap and chart js.
The backend utilises beat schedular to perform daily metrics and store in the database.

### Payments
Models for storing payment information and functions to make payments by forwarding requests to the upstream Paynow server and polling accirding to the beat schedule.

### User accounts
Manages user information. Provides urls for signing up, reseting passwords

### Whats app
Has url used by whatsapp webhook and functions used by other apps to send whatsapp messages. Models used to deserialise whatsapp payload and extract information in the payload. Makes requests to whatsapp endpoints.

### ZimGPT
Models for storing user data on use of AI services. Provides urls for the web interphase including websocket connections for streaming.




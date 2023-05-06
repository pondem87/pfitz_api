from __future__ import absolute_import, unicode_literals
from pfitz_api.celery import celery_app
from .aux_func import send_text, send_template

import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="send_app_text")
def send_app_text(user_num: str, message: str, wamid: str):
    send_text(user_num, message, wamid)


@celery_app.task(name="send_app_template")
def send_app_template(user_num: str, template: str, params, lang: str):
    send_template(user_num, template, params, lang)
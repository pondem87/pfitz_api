from __future__ import absolute_import, unicode_literals
from pfitz_api.celery import celery_app
from .aux_func import send_text, send_template
from decouple import config

import logging

wa_temp_lang = config('WA_TEMPLATE_DEFAULT_LANG')

logger = logging.getLogger(__name__)

@celery_app.task(name="send_app_text")
def send_app_text(user_num: str, message: str, wamid: str=None):
    send_text(user_num, message, wamid)


@celery_app.task(name="send_app_template")
def send_app_template(user_num: str, template: str, params=None, lang: str=wa_temp_lang):
    send_template(user_num, template, params, lang)
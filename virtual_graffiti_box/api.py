from django.http import HttpResponse
from django.shortcuts import render
import base64
import time
import pytz

from datetime import datetime, timedelta
import random

BASE_URL = 'api/v1/'
pst_timezone = pytz.timezone('America/Los_Angeles')

generated_codes = {}

def generate_code(user_id):
    current_time = datetime.now().astimezone(pst_timezone)
    code = str(10000 + random.randint(0, 89999))
    expiration_time = current_time + timedelta(minutes=5)
    generated_codes[user_id] = {'code': code, 'expiration_time': expiration_time}
    return code, expiration_time

def get_user_code(user_id):
    if user_id in generated_codes and generated_codes[user_id]['expiration_time'] > datetime.now().astimezone(pst_timezone):
        return generated_codes[user_id]['code'], generated_codes[user_id]['expiration_time']
    else:
        return generate_code(user_id)

def valid_code(code):
    current_time = datetime.now().astimezone(pst_timezone)

    for user_id, data in generated_codes.items():
        if data['code'] == code:
            if data['expiration_time'] > current_time:
                return True
            else:
                del generated_codes[user_id]
                break

    return False

def validate_code(request, code):
    code = str(code)
    if valid_code(code):
        user_id = request.session.get('user_id')
        generated_codes[user_id]['expiration_time'] = datetime.now().astimezone(pst_timezone) + timedelta(hours=12)
        return HttpResponse(status=200)
    return HttpResponse(status=400)
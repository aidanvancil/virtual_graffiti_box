from django.http import HttpResponse
from django.shortcuts import render
import base64
import time
import json
import pytz
import hashlib
from app.models import UserProfile, Laser
from datetime import datetime, timedelta
import random
from . import settings as django_settings

HOST = "http://localhost:8000" if django_settings.DEBUG else "https://virtual-graffiti-box.onrender.com"
BASE_URL = 'api/v1/'
pst_timezone = pytz.timezone('America/Los_Angeles')

generated_codes = {}
generated_user_ids = {}
first_time_generation = set()


def cleanup_expired_codes():
    current_time = datetime.now(pst_timezone)
    expired_user_ids = []
    for user_id, data in generated_codes.items():
        if data['expiration_time'] <= current_time:
            expired_user_ids.append(user_id)

    # Delete expired codes along with associated lasers
    for user_id in expired_user_ids:
        del generated_codes[user_id]
        for code, uid in generated_user_ids.items():
            if uid == user_id:
                del generated_user_ids[code]
                break
        
        first_time_generation.remove(code)
        UserProfile.objects.filter(code=user_id).delete()
        Laser.objects.filter(code=code).delete()

def generate_code(user_id):
    current_time = datetime.now().astimezone(pst_timezone)
    code = None
    while True:
        code = str(10000 + random.randint(0, 89999))
        if code not in first_time_generation:
            break 
        else:
            cleanup_expired_codes()
    expiration_time = current_time + timedelta(minutes=5)
    generated_codes[user_id] = {'code': code, 'expiration_time': expiration_time}
    return str(code), expiration_time

def get_user_code(user_id):
    if user_id in generated_codes and generated_codes[user_id]['expiration_time'] > datetime.now().astimezone(pst_timezone):
        return generated_codes[user_id]['code'], generated_codes[user_id]['expiration_time']
    else:
        code, expiration = generate_code(user_id)
        generated_user_ids[code] = user_id
        return code, expiration

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
        user_id = generated_user_ids[code]
        user_expiration_time = generated_codes[user_id]['expiration_time']    
        current_time = datetime.now(pst_timezone)        
        expiration_threshold = current_time + timedelta(minutes=30)        
        if user_expiration_time <= expiration_threshold:
            user_expiration_time += timedelta(hours=4)

        if code not in first_time_generation:
            Laser.objects.create(id='Red', code=code)
            Laser.objects.create(id='Green', code=code)
            Laser.objects.create(id='Purple', code=code)
            first_time_generation.add(code)
        return HttpResponse(status=200)
    return HttpResponse(status=400)

def generate_settings_url(first_name, last_name, laser_pointer, code):
    print(first_name, last_name, laser_pointer)
    laser_pointer = laser_pointer.capitalize()
    url = None
    try:
        if first_name and last_name and laser_pointer:
            laser = Laser.objects.get(id=laser_pointer, code=code)
            UserProfile.objects.create(first_name=first_name, last_name=last_name, laser=laser, code=code)
            base64_user_identifier = base64.b64encode(f"{first_name}_{last_name}_{laser_pointer}".encode('utf-8')).decode('utf-8')
            url = f"{HOST}/settings/{base64_user_identifier}/{code}"
    except Exception as e:
        print(e)
        pass
    print(url)
    return url

def fetch_settings_url(request, code):
    if request.method == 'GET':
        code = str(code)
        first_name = request.GET.get('firstname')
        last_name = request.GET.get('lastname')
        laser_pointer = request.GET.get('laser')
        if valid_code(code):
            user_id = generated_user_ids[code]
            generated_codes[user_id]['expiration_time'] = datetime.now().astimezone(pst_timezone) + timedelta(hours=4)
            url = generate_settings_url(first_name, last_name, laser_pointer, code)
            if url:
                response_data = {'url': url}
                return HttpResponse(json.dumps(response_data), content_type='application/json', status=200)
            else:
                return HttpResponse(json.dumps({'error': 'Failed to generate settings URL'}), content_type='application/json', status=500)
    return HttpResponse(status=400)

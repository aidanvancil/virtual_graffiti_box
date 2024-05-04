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
    """
    Cleans up expired user codes and associated data.
    """
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
        UserProfile.objects.filter(code=code).delete()
        Laser.objects.filter(code=code).delete()

def generate_code(user_id):
    """
    Generates a unique code for a user.

    Args:
        user_id (str): The unique identifier for the user.

    Returns:
        tuple: A tuple containing the generated code and its expiration time.
    """
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
    """
    Retrieves the user code associated with the provided user identifier.

    Args:
        user_id (str): The unique identifier for the user.

    Returns:
        tuple: A tuple containing the user code and its expiration time.
    """
    if user_id in generated_codes and generated_codes[user_id]['expiration_time'] > datetime.now().astimezone(pst_timezone):
        return generated_codes[user_id]['code'], generated_codes[user_id]['expiration_time']
    else:
        code, expiration = generate_code(user_id)
        generated_user_ids[code] = user_id
        return code, expiration

def valid_code(code):
    """
    Checks if a code is valid and not expired.

    Args:
        code (str): The code to validate.

    Returns:
        bool: True if the code is valid and not expired, False otherwise.
    """
    current_time = datetime.now().astimezone(pst_timezone)
    for user_id, data in generated_codes.items():
        if str(data['code']) == str(code):
            if data['expiration_time'] > current_time:
                return True
            else:
                del generated_codes[user_id]
                break

    return False

def validate_code(request, code):
    """
    Validates a user code and updates the associated data if necessary.

    Args:
        request (HttpRequest): The HTTP request object.
        code (str): The code to validate.

    Returns:
        HttpResponse: An HTTP response indicating the result of the validation.
    """
    code = str(code)
    if valid_code(code):
        user_id = generated_user_ids[code]
        user_expiration_time = generated_codes[user_id]['expiration_time']    
        current_time = datetime.now(pst_timezone)        
        expiration_threshold = current_time + timedelta(minutes=30)        
        if user_expiration_time <= expiration_threshold:
            user_expiration_time += timedelta(hours=4)

        if code not in first_time_generation:
            Laser.objects.create(uid='Red', code=code)
            Laser.objects.create(uid='Green', code=code)
            Laser.objects.create(uid='Purple', code=code)
            first_time_generation.add(code)
        response = HttpResponse(status=200)
        return response
    response_data = json.dumps({"error": "Invalid Code. See server invalidation.", "code": code})
    response = HttpResponse(response_data, content_type="application/json", status=400)
    return response

def generate_settings_url(first_name, last_name, laser_pointer, code):
    """
    Generates a settings URL for a user.

    Args:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        laser_pointer (str): The pointer of the laser associated with the user.
        code (str): The user code.

    Returns:
        str: The generated settings URL.
    """
    url = None
    try:
        if first_name and last_name and laser_pointer:
            laser = Laser.objects.get(uid=laser_pointer, code=code)
            UserProfile.objects.create(first_name=first_name, last_name=last_name, laser=laser, code=code)
            base64_user_identifier = base64.b64encode(f"{first_name}_{last_name}_{laser_pointer}".encode('utf-8')).decode('utf-8')
            url = f"{HOST}/settings/{base64_user_identifier}/{code}"
    except Exception as e:
        print(e)
        pass
    return url

def fetch_settings_url(request, code):
    """
    Fetches the settings URL for a user.

    Args:
        request (HttpRequest): The HTTP request object.
        code (str): The user code.

    Returns:
        HttpResponse: An HTTP response containing the settings URL or an error message.
    """
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

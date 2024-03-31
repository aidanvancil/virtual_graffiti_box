from django.http import HttpResponse
import base64
import time
from datetime import datetime, timedelta
BASE_URL = 'api/v1/'

generated_codes = {}
validated_codes = {}

def generate_code():
    current_time = datetime.now()
    code =  str(10000 + int(time.time()) % 90000)
    generated_codes[code] = current_time
    return code

def remove_expired_codes():
    current_time = datetime.now()
    expired_validated_codes = [code for code, creation_time in validated_codes.items() if current_time - creation_time > timedelta(hours=12)]
    for code in expired_validated_codes:
        del validated_codes[code]
    
    expired_generated_codes = [code for code, creation_time in generated_codes.items() if current_time - creation_time > timedelta(minutes=5)]
    for code in expired_generated_codes:
        del generated_codes[code]

def valid_code(code):
    current_time = datetime.now()

    if code in validated_codes:
        creation_time = validated_codes[code]
        if current_time - creation_time <= timedelta(hours=12):
            return True
        else:
            del validated_codes[code]
    elif code in generated_codes:
        creation_time = generated_codes[code]
        if current_time - creation_time <= timedelta(minutes=5):
            return True
        else:
            del generated_codes[code]
    return False

def code_validation(request):
    if request.method == 'GET':
        code = request.GET.get('code')
        remove_expired_codes()
        if code and valid_code(code):
            validated_codes[code] = datetime.now()
            return HttpResponse(status=200)
    return HttpResponse(status=400)


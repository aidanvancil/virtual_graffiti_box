from django.shortcuts import render
from django.http import HttpResponse
from app.models import UserProfile, Laser
import base64
import datetime
import time
from . import api

def admin_panel(request):
    user_id = request.session.get('user_id')
    if not user_id:
        user_id = base64.b64encode(str(time.time()).encode()).decode()[:10]
        request.session['user_id'] = user_id

    code, expiration = api.get_user_code(user_id)
    expiration = expiration.strftime("%B %d, %Y @ %l:%M %p")
    context = {
        'code': code,   
        'countdown': expiration
    }

    return render(request, 'admin_panel.html', context)

def settings(request, user_identifier, code):
    try:
        user_identifier_decoded = base64.b64decode(user_identifier).decode('utf-8')
        first_name, last_name, laser_pointer_id = user_identifier_decoded.split('_')
    except:
        return errors(request, error_code=302)
    
    try:
        laser_pointer = Laser.objects.get(uid=laser_pointer_id, code=code)
        user = UserProfile.objects.get(first_name=first_name, last_name=last_name, laser=laser_pointer, code=code)
    except UserProfile.DoesNotExist:
        print("User profile does not exist.")
        return errors(request, error_code=302)
    except Laser.DoesNotExist:
        print("Laser does not exist.")
        return errors(request, error_code=302)
    except Exception as e:
        print("Error retrieving user profile:", e)
        return errors(request, error_code=500)
    
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'laser_pointer': user.laser.uid,
    }

    return render(request, 'settings.html', context)


def errors(request, error_code=404):
    context = {
        'error_code': error_code
    }
    response = render(request, 'errors.html', context)
    response.status_code = error_code
    response['Location'] = '/errors/' + str(error_code)
    return response
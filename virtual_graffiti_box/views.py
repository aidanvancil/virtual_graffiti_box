from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from app.models import UserProfile, Laser
import json
import base64
import datetime
import time
from . import api, settings

HOST = "http://localhost:8000" if settings.DEBUG else "https://virtual-graffiti-box.onrender.com"

def admin_panel(request):
    user_id = request.session.get('user_id')
    if not user_id:
        user_id = base64.b64encode(str(time.time()).encode()).decode()[:10]
        request.session['user_id'] = user_id

    code, expiration = api.get_user_code(user_id)
    expiration = expiration.strftime("%B %d, %Y @ %l:%M %p")
    context = {
        'code': code,   
        'countdown': expiration,
        'host': HOST
    }

    return render(request, 'admin_panel.html', context)

def get_laser(request, laser_id, code):
    if request.method == 'GET':
        try:
            laser = Laser.objects.get(code=code, uid=laser_id)
        except Laser.DoesNotExist:
            return errors(request, error_code=302)

        return JsonResponse({
            'color': laser.color,
            'size': laser.size,
        })
        
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def set_laser_color(request, laser_id, code):
    if api.valid_code(code):
        data = json.loads(request.body)
        laser = Laser.objects.get(code=code, uid=laser_id)
        laser.color = data['data']
        laser.save()
        return JsonResponse({'success': True}, status=200)
    return JsonResponse({'success': False}, status=404)

def set_laser_size(request, laser_id, code):
    if api.valid_code(code):
        data = json.loads(request.body)
        laser = Laser.objects.get(code=code, uid=laser_id)
        laser.size = data['data']
        laser.save()
        return JsonResponse({'success': True}, status=200)
    return JsonResponse({'success': False}, status=404)

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
        'host': HOST,
        'code': code
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
from django.shortcuts import render
from . import api
HOST = "localhost:8000"

#UC01, FR4
# @login_required(login_url='login')
# def signup(request):
#     if request.method == 'POST':
#         first_name = request.POST.get('firstname')
#         last_name = request.POST.get('lastname')
#         laser_pointer = request.POST.get('laser')
#         laser = Laser.objects.get(id=laser_pointer)

#         UserProfile.objects.create(first_name=first_name, last_name=last_name, laser=laser)
#         base64_user_identifier = base64.b64encode(f"{first_name}_{last_name}_{laser_pointer}".encode('utf-8')).decode('utf-8')
#         redirect_url = f"http://{HOST}/settings/{base64_user_identifier}"
       
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
        
#         qr.add_data(redirect_url)
#         qr.make(fit=True)

#         img = qr.make_image(fill_color="black", back_color="white")

#         buffer = BytesIO()
#         img.save(buffer)
#         qr_code_image = buffer.getvalue()

#         qr_code_base64 = base64.b64encode(qr_code_image).decode('utf-8')

#         context = {
#             'qr_code_base64': qr_code_base64,
#         }

#         return render(request, 'signup.html', context)\
            
#     else:  
#         lasers_without_users = Laser.objects.filter(userprofile__isnull=True)
#         context = {
#             'available_lasers': list(lasers_without_users.values_list('id', flat=True))
#         }
        
#     return render(request, 'signup.html', context)

def admin_panel(request):
    code = api.generate_code()
    context = {'code': code}

    return render(request, 'admin_panel.html', context)


def errors(request, error_code=404):
    context = {
        'error_code': error_code
    }
    response = render(request, 'errors.html', context)
    response.status_code = error_code
    response['Location'] = '/errors/' + str(error_code)
    return response
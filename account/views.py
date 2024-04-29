from django.shortcuts import render

# Create your views here.

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .utils import password_reset_token
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.core.mail import send_mail
from . import utils as user_utils
from management import models as management_models
import datetime


def index(request):
    user = request.user
    if user.userprofile.role == manager:
        all_sales_advisors = UserProfile.objects.filter(role=sales_advisor).count()
        today_shifts = management_models.Shift.objects.filter(date=datetime.date.today()).count()
        today_announcements = management_models.Announcement.objects.filter(
            created_at__date=datetime.date.today()).count()
        today_requests = management_models.Request.objects.filter(created_at__date=datetime.date.today()).count()
        context = {
            'user': request.user,
            'nav_class': 'dashboard',
            'is_admin': True,
            "all_sales_advisors": all_sales_advisors,
            "today_shifts": today_shifts,
            "today_announcements": today_announcements,
            "today_requests": today_requests,
            'full_name': request.user.get_full_name(),

        }
        return render(request, 'admin/panel.html', context)
    else:
        context = {
            'user': request.user,
            'is_admin': False,
            'full_name': request.user.get_full_name(),
        }
        return render(request, 'admin/sa_panel.html', context)


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', None)
        middle_name = request.POST.get('middle_name', None)
        surname = request.POST.get('surname', None)
        email = request.POST.get('employee_email', None)
        phone = request.POST.get('employee_phone', None)
        address = request.POST.get('employee_address', None)
        employee_number = request.POST.get('employee_number', None)
        department = request.POST.get('department', None)
        password = request.POST.get('password', None)
        user_obj = User.objects.create(email=email, first_name=first_name, last_name=surname, username=employee_number
                                       )
        user_obj.set_password(password)
        user_obj.save()
        userprofile_obj = UserProfile.objects.create(user=user_obj, phone=phone, address=address, department=department,
                                                     employee_number=employee_number, middle_name=middle_name,
                                                     role=sales_advisor)
        return redirect('login')
    return render(request, 'account/signup.html')


def login_view(request):
    if request.method == 'POST':
        employee_number = request.POST.get('employee_number')
        password = request.POST.get('password')
        user = authenticate(request, username=employee_number, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, " Login Successfully.")
            return redirect('index')  # Redirect to your desired homepage

        else:
            print("Invalid credentials")
            # Invalid credentials
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'account/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logout Successfully!")
    return redirect('login')  # Redirect to login page after logout


def recover_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'email is not valid.')
            return redirect('forgot-password')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            token = password_reset_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk)),
            uid = uid[0]
            recover_password_link = "{}://{}{}".format(request.scheme, request.get_host(),
                                                       reverse("reset_password", args=(uid, token,)))
            subject = 'Reset your password'
            message = f'Hi {user.username}, Please use the link below to reset your password  {recover_password_link}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(
                subject, message, email_from, recipient_list, fail_silently=False
            )
            messages.success(request, 'mail has been sent successfully.')
            return redirect('password_reset_done')
        else:
            messages.error(request, 'User not found against this email!')
            return redirect('forgot-password')
    else:
        return render(request, 'forgot-pwd.html', {'title': "Forgot Password"})


def reset_password(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
    if user is not None and password_reset_token.check_token(user, token):
        if request.method == 'POST':
            params = request.POST
            password = params['password1']
            password2 = params['password2']
            if password == password2:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password update successfully! Please login.')
                return redirect('login')
            else:
                messages.error(request, 'Password and confirm password not match!')
                return redirect('reset_password', uidb64=uidb64, token=token)

        else:
            return render(request, 'reset_password.html')
    else:
        message = messages.error(request, 'Password not match!')


def password_reset_done(request):
    return render(request, 'reset_password_done.html')

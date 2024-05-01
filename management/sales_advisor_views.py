import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.core.mail import send_mail
from . import models as management_models
from account import models as account_models
from django.db.models import Q
from . import forms as management_forms, tables as management_tables
from account import models as account_models
from employee_management import utils as em_utils_


def next_shifts(request):
    next_shifts = management_models.Shift.objects.filter(userprofile=request.user.userprofile).order_by('-id')
    print("these are the shifts======", next_shifts)
    context = {
        'next_shifts': next_shifts,
        'nav_class': 'next_shifts',
        'form_title': 'Next Shifts',
        'full_name': request.user.get_full_name(),

    }

    return render(request, 'sa_add_or_edit.html', context)


def task_overview(request):
    tasks = management_models.Task.objects.filter(userprofile=request.user.userprofile).order_by('-id')
    print("these are the shifts======", next_shifts)
    context = {
        'tasks': tasks,
        'nav_class': 'tasks_overview',
        'form_title': 'Tasks View',
        'full_name': request.user.get_full_name(),

    }

    return render(request, 'sa_add_or_edit.html', context)


def mark_task_as_complete(request, id):
    task_obj = management_models.Task.objects.get(id=id)
    task_obj.is_completed = True
    task_obj.save()
    return redirect('task-overview')


def sa_latest_announcements(request):
    announcements = management_models.Announcement.objects.all().order_by('-created_at')
    context = {
        'announcements': announcements,
        'nav_class': 'latest_announements',
        'form_title': 'Latest Announcements',
        'full_name': request.user.get_full_name(),

    }
    return render(request, 'sa_add_or_edit.html', context)


def sa_leave_request_status(request):
    requests = management_models.Request.objects.filter(userprofile=request.user.userprofile).order_by('-id')
    context = {
        'requests': requests,
        'nav_class': 'leave_request_status',
        'form_title': 'Leave Request Status',
        'links': [
            {
                'button': "Add Request",
                'href': reverse('sa-add-request'),
                'color': 'blue'
            },

        ],
        'full_name': request.user.get_full_name(),

    }
    return render(request, 'sa_add_or_edit.html', context)


def add_request(request):
    form = management_forms.AddRequestForm()
    if request.method == "POST":
        title = request.POST.get('title', None)
        description = request.POST.get('description', None)
        request_obj = management_models.Request.objects.create(userprofile=request.user.userprofile, title=title,
                                                               description=description)
        messages.success(request, 'Request Submitted Successfully')
    context = {
        'form': form,
        'form_title': "Add New Request",
        "nav_class": "leave_request_status",
        'links': [

            {
                'button': "Back",
                'href': reverse('sa-leave-request-status'),
                'color': 'red'
            },
        ],
        'full_name': request.user.get_full_name(),

    }
    return render(request, 'sa_add_or_edit.html', context)


def sa_messages(request):
    if request.method == "POST":
        return render(request, 'leave_manager.html')
    form = management_forms.MessageForm()
    form.fields['user'].queryset = account_models.UserProfile.objects.all().exclude(user_id=request.user.id)
    users = account_models.UserProfile.objects.all().exclude(user_id=request.user.id)
    all_receiver_groups = management_models.ReceiverGroup.objects.filter(users=request.user.userprofile, is_group=True)
    have_messages = False
    allgroups = []
    for group in all_receiver_groups:
        allgroups.append({"name": group.name, "id": group.id,
                          "unread_messages": em_utils_.get_group_unread_messages(request, group.id)})
    allusers = []
    for user in users:
        if em_utils_.get_unread_messages(user, request.user.userprofile) > 0:
            have_messages = True
        allusers.append(
            {"name": user.user.get_full_name(), "id": user.user.id,
             "unread_messages": em_utils_.get_unread_messages(user, request.user.userprofile)})

    print("users====", allgroups)
    context = {
        "form": form,
        "all_users": allusers,
        "all_groups": allgroups,
        "have_messages": have_messages,
        "request": request,
        "sales_advisor": True,
        'nav_class': "messages",
        'links': [
            {
                'button': "Add Group",
                'href': reverse('sa-add-request'),
                'color': 'blue'
            },

        ],
    }
    return render(request, 'admin/messages.html', context)


def mark_message_as_read(request):
    sender = request.GET.get('sender', None)
    sender = account_models.UserProfile.objects.get(user_id=sender)
    receiver = request.user.userprofile
    em_utils_.mark_messages_as_read(sender, receiver)
    return JsonResponse({"status": "success"})


def mark_group_message_as_read(request):
    group = request.GET.get('group', None)
    em_utils_.mark_group__messages_as_read(request, group)
    return JsonResponse({"status": "success"})

from django.contrib.auth.models import User
from django.db import models
from management import models as management_models

# Create your models here.


sales_advisor = 'Sales Advisor'
manager = 'Manager'
user_role_choices = [
    (sales_advisor, sales_advisor),
    (manager, manager)
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    middle_name = models.CharField(max_length=50, blank=True)
    employee_number = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=50, blank=True, choices=user_role_choices, default=sales_advisor)

    def __str__(self):
        return self.user.get_full_name()

    @property
    def get_unread_messages(self):
        unread_messages = 0
        receiver_objs = management_models.ReceiverGroup.objects.filter(users=self)
        for receiver_obj in receiver_objs:
            messages = management_models.Message.objects.filter(receiver=receiver_obj).order_by(
                'created_at')
            for message in messages:
                if message.sender.user_id != self.user.id:
                    if not message.is_read:
                        unread_messages += 1
        return unread_messages

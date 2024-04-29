from django.contrib import admin

# Register your models here.
from . import models as account_models

admin.site.register(account_models.UserProfile)

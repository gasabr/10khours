from django.contrib.auth.models import User
from django.contrib import admin
from django.db import models
from oauth2client.contrib.django_util.models import CredentialsField


class CredentialsModel(models.Model):
    credentials = CredentialsField()
    user = models.OneToOneField(User, primary_key=True)

    class Meta:
        db_table = 'credentials'


# to be able to see credentials in admin
class CredentialsAdmin(admin.ModelAdmin):
    pass

admin.site.register(CredentialsModel, CredentialsAdmin)

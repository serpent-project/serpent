from django.db import models

class Account(models.Model):
    username = models.CharField(max_length=30)
    password = models.PasswordField()


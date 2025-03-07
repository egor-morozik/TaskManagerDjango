from django.db import models

class UserManager(models.Manager):
    def create_user(self, email, password):
        user = self.model(email=email, password=password)
        user.save(using=self._db)
        return user

class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    objects = UserManager()
    
from django.db import models
from django.contrib.auth.models import AbstractUser


class Techie(AbstractUser):
    email = models.EmailField(unique=True, null=True)
    name = models.CharField(max_length=150, null=True)
    username = models.CharField(max_length=150, unique=True, null=True)
    avatar = models.ImageField(null=False, default='avatar.svg')
    user_plan = models.CharField(max_length=100, null=True, default="basic")


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

class File(models.Model):
    host = models.ForeignKey(Techie, on_delete=models.CASCADE, null=True)
    fname = models.CharField(max_length=120, null=True)
    file_content = models.FileField(upload_to='files', null=True)
    file_text = models.TextField(null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    file_tags = models.TextField(null=True, blank=True)
    file_summary = models.TextField(null=True, blank=True)

class Dialogue(models.Model):
    host = models.ForeignKey(Techie, on_delete=models.CASCADE, null=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    query = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

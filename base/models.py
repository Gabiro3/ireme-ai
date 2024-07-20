from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class Techie(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    name = models.CharField(max_length=150, unique=True, null=True)
    avatar = models.ImageField(null=False, default='avatar.svg') #Change avatar
    user_plan = models.CharField(max_length=100, null=True, default="basic")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    query = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

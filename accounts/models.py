from django.db import models
from .detect_face import refresh_pickle
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class UserAccounts(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Invalid format, ex: '+999999999'.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O','Other')

    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob=models.DateTimeField(null=True,blank=True)
    is_uploaded=models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()


def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.user.email, ext)
    print(instance.user.email)
    print(os.path.join('media','security_picture', filename))
    return os.path.join('media','security_picture', filename.replace("@","__"))

class ProfilePhoto(models.Model):
    user = models.ForeignKey(UserAccounts,on_delete=models.CASCADE)
    profile = models.ImageField(upload_to='media/profile/',default="media/default_profile.jpg")
    security = models.ImageField(upload_to=content_file_name,default="default_secure.jpg")
    face_uploaded = models.BooleanField(default=False)

@receiver(post_delete, sender=ProfilePhoto)
def photo_delete(sender, instance, **kwargs):
    instance.profile.delete(False) 
    instance.security.delete(False) 
    

    refresh_pickle()



class Posts(models.Model):
    user = models.ForeignKey(UserAccounts,on_delete=models.CASCADE)
    posted_image = models.ImageField(upload_to='media/posted_images/')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_liked(self):
        objects = Like.objects.filter(post=self).values_list('user', flat=True)
        return objects

@receiver(post_delete, sender=Posts)
def submission_delete(sender, instance, **kwargs):
    instance.posted_image.delete(False) 

class Comments(models.Model):
    user = models.ForeignKey(UserAccounts,on_delete=models.CASCADE)
    post = models.ForeignKey(Posts,on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def class_name(self):
        return self.__class__.__name__

class Like(models.Model):
    user = models.ForeignKey(UserAccounts,on_delete=models.CASCADE)
    post = models.ForeignKey(Posts,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def class_name(self):
        return self.__class__.__name__

class Friends(models.Model):
    follower =  models.ForeignKey(UserAccounts,on_delete=models.CASCADE, related_name="follower")
    following =  models.ForeignKey(UserAccounts,on_delete=models.CASCADE, related_name="following")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Can't follow yourself ")

        if following.objects.filter(follower=follower,following=following):
            raise ValidationError("you are already following this person")
        return super().clean()
    
    def class_name(self):
        return self.__class__.__name__

class FacesPermission(models.Model):
    post = models.ForeignKey(Posts, on_delete = models.CASCADE)
    user = models.ForeignKey(UserAccounts, on_delete = models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    w = models.IntegerField()
    h = models.IntegerField()
    blurred = models.BooleanField(default = False)
    allowed = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add= True)

    def class_name(self):
        return self.__class__.__name__

class Chat(models.Model):
    sender = models.ForeignKey(UserAccounts, on_delete= models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(UserAccounts, on_delete= models.CASCADE, related_name="receiver")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.sender.email} {self.receiver.email} {self.message}"
    




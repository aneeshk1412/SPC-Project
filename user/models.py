from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class DirFile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parentId = models.PositiveIntegerField()
    name = models.CharField(max_length=5000)
    md5code = models.CharField(max_length=5000)
    pathLineage = models.TextField()
    TYPE = ( ('f', 'file'), ('d', 'directory'), )
    dorf = models.CharField(
        max_length=1,
        choices=TYPE,
        blank=False,
        default='f',
        help_text='File or Directory',
    )
    fileContent = models.BinaryField(max_length=10000000, editable=True)
    modifiedTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        uname = str(self.owner)
        nme = str(self.name)
        path = str(self.pathLineage)
        time = str(self.modifiedTime)
        df = str(self.dorf)
        res = "Username: " + uname + ", Name: " + nme + ", Dir or File: " + df + ", Path: " + path + ", ModifiedTime: " + time
        return res


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    locked = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
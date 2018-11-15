from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class DirFile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parentId = models.PositiveIntegerField()
    name = models.CharField(max_length=5000)
    depth = models.PositiveIntegerField()
    pathLineage = models.TextField()
    TYPE = ( ('f', 'file'), ('d', 'directory'), )
    dorf = models.CharField(
        max_length=1,
        choices=TYPE,
        blank=False,
        default='f',
        help_text='File or Directory',
    )
    fileContent = models.TextField()
    modifiedTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        uname = str(self.owner)
        nme = str(self.name)
        path = str(self.pathLineage)
        time = str(self.modifiedTime)
        df = str(self.dorf)
        res = "Username: " + uname + " Name: " + nme + "Dir or File: " + df + ", Path: " + path + ", ModifiedTime: " + time
        return res


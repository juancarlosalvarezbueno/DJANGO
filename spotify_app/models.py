from django.db import models

class Usuario(models.Model):
     user = models.CharField(max_length=100, unique=True)
     songs = models.JSONField(default=list)

     def __str__(self):
         return self.user

class Song(models.Model):
    song_name = models.CharField(max_length=255)

    def __str__(self):
        return self.song_name
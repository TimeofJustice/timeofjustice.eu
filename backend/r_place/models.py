from django.db import models

# Create your models here.
class Message(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"Message {self.id} in room {self.room}: {self.message[:50]}..."

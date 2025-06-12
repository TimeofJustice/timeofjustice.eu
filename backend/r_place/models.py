from django.db import models
from django.utils import timezone


# Create your models here.
class Message(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return f"Message {self.id} in room {self.room}: {self.message[:50]}..."


class Cell(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    color = models.CharField(max_length=7)
    last_modified = models.DateTimeField(editable=False)

    class Meta:
        ordering = ('-last_modified', 'x', 'y')
        verbose_name = "  Cell"
        verbose_name_plural = "  Cells"

    def __str__(self):
        return f"{self.color} ({self.x}, {self.y})"

    def save(self, *args, **kwargs):
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)

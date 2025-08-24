from django.db import models
from django.utils import timezone


class Canvas(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100, unique=True, default="Default Canvas")
    width = models.IntegerField(default=1000)
    height = models.IntegerField(default=1000)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Canvas"
        verbose_name_plural = "Canvases"
        ordering = ('-active', 'id')

    def __str__(self):
        return f"{self.name} ({self.width}x{self.height})"


class RenderedCanvas(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    canvas = models.ForeignKey(Canvas, on_delete=models.CASCADE, related_name='rendered_canvases')
    image_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Rendered Canvas"
        verbose_name_plural = "Rendered Canvases"

    def __str__(self):
        return f"Rendered {self.canvas.name} at {self.created_at}"


class Cell(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    color = models.CharField(max_length=7)
    canvas = models.ForeignKey(Canvas, on_delete=models.CASCADE, related_name='cells', default=None)
    last_modified = models.DateTimeField(editable=False)

    class Meta:
        ordering = ('-last_modified', 'x', 'y')
        verbose_name = "  Cell"
        verbose_name_plural = "  Cells"

    def __str__(self):
        return f"{self.color} ({self.x}, {self.y})"

    def save(self, *args, **kwargs):
        self.last_modified = timezone.now()
        if not self.canvas_id:
            active_canvas = Canvas.objects.filter(active=True).first()
            self.canvas_id = active_canvas.id if active_canvas else None
            if not self.canvas_id:
                raise ValueError("No active canvas found.")
        super().save(*args, **kwargs)

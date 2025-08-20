from django.db import models


class Design(models.Model):
    id = models.AutoField(primary_key=True)
    page_color = models.CharField(max_length=7, default="#ffbaba")
    background_color = models.CharField(max_length=7, default="#fff")
    stamp_color = models.CharField(max_length=7, default="#e5b473")
    accent_color = models.CharField(max_length=7, default="#e57373")
    text_color = models.CharField(max_length=7, default="#333333")
    icon = models.CharField(max_length=50, default="twemoji:teddy-bear")

    def __str__(self):
        return f"Design {self.id}"

    def json(self):
        return {
            "id": self.id,
            "pageColor": self.page_color,
            "backgroundColor": self.background_color,
            "stampColor": self.stamp_color,
            "accentColor": self.accent_color,
            "textColor": self.text_color,
            "icon": self.icon,
        }


class Postcard(models.Model):
    id = models.CharField(primary_key=True, max_length=6)
    message = models.TextField(default="Hallo, dies ist eine Postkarte")
    greetings = models.CharField(max_length=50, default="Mit viel Liebe, dein Freund")
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    amount_reports = models.IntegerField(default=0)
    showcased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Postcard {self.id}"

    def json(self):
        return {
            "id": self.id,
            "message": self.message,
            "greetings": self.greetings,
            "design": self.design.json() if self.design else None,
        }

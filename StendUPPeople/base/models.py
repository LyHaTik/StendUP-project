from django.db import models


class Client(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True)
    tg_id = models.IntegerField()
    tg_username = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    joke = models.TextField()

    def __str__(self) -> str:
        return f'{self.tg_username}'
    
    
class Follow(models.Model):
    follow = models.BooleanField(default=False)


class Subject(models.Model):
    text = models.CharField(max_length=100, blank=True, null=True)
    callback = models.CharField(max_length=100, blank=True, null=True)
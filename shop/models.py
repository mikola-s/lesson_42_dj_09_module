from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import localtime
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name='profile')
    cash = models.PositiveIntegerField(default=10000)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=256)
    price = models.PositiveIntegerField()
    photo = models.FileField(upload_to='static/images/')
    count = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.pk} {self.name}"


class Purchase(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name='products')
    count = models.PositiveIntegerField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        time = localtime(self.time).strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.buyer.username} / ({self.count}) {self.product.name} -- {time}"


class Return(models.Model):
    purchase = models.OneToOneField(to=Purchase, on_delete=models.CASCADE, related_name='purchase')
    time = models.DateTimeField(auto_now_add=True)

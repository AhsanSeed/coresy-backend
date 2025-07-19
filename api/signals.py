# api/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Wallet, UserPoints

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created and not Wallet.objects.filter(user=instance).exists():
        Wallet.objects.create(user=instance)
@receiver(post_save, sender=User)
def create_points(sender, instance, created, **kwargs):
    if created:
        UserPoints.objects.create(user=instance)
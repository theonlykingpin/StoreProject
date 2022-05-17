from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Customer


@receiver(post_save, sender=get_user_model())
def create_customer_for_new_user(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

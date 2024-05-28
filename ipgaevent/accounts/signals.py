from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User


# @receiver(post_save, sender=User)
# def create_user(sender, instance, created, **kwargs):
#     print("Inside Signal")
#
#     if created:
#         instance.reg_id = f"BDS2024{instance.id}"
#         instance.save()
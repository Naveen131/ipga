from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User, Payment
from accounts.payment import send_registration_confirmation_email


# @receiver(post_save, sender=User)
# def create_user(sender, instance, created, **kwargs):
#     print("Inside Signal")
#
#     if created:
#         instance.reg_id = f"BDS2024{instance.id}"
#         instance.save()


@receiver(post_save, sender=Payment)
def create_payment(sender, instance, created, **kwargs):
    print("Inside Signal")

    if instance.status == "Success":
        send_registration_confirmation_email(instance.user, instance)
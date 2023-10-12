# signals.py
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models.signals import post_delete, post_init, post_save
from django.dispatch import receiver
from salesman.core.utils import get_salesman_model
from salesman.orders.signals import status_changed


BasketItem = get_salesman_model("BasketItem")
                                
from .models import ShopSettings


Order = get_salesman_model("Order")


def get_email_settings():
    shop_email_settings = ShopSettings.load()
    notify_emails = shop_email_settings.notify_email_addresses
    if notify_emails:
        notify_emails = shop_email_settings.notify_email_addresses.split(",")
    reply_to = [shop_email_settings.reply_to or settings.DEFAULT_FROM_EMAIL]
    return notify_emails, reply_to


@receiver(status_changed)
def send_notification(sender, order, new_status, old_status, **kwargs):
    """
    Send notification to customer when order is moved to completed.
    """
    if new_status in [order.Status.COMPLETED, order.Status.PROCESSING]:
        reply_to, _ = get_email_settings()
        if new_status == order.Status.COMPLETED:
            subject = f"Order '{order.ref}' is completed"
            message = "Thank you for your order! Your order is now complete."

        elif new_status == order.Status.PROCESSING:
            subject = f"Order '{order.ref}' is being processed"
            message = "Thank you for your order!  Your order is being processed."

        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            reply_to=reply_to,
        )
        email.send()


@receiver(post_save, sender=Order)
def send_new_order_notifications(sender, instance, created, **kwargs):
    """
    Send notification to customer when order is first created
    """
    if created:
        notify_emails, reply_to = get_email_settings()

        subject = f"Order '{instance.ref}' has been received"
        if instance.status == instance.Status.HOLD:
            message = "Thank you for your order! Your order will be completed when payment has been received."
        else:
            message = "Thank you for your order! Your order is being processed."

        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            reply_to=reply_to,
        )
        email.send()

        if notify_emails:
            subject = f"New shop order '{instance.ref}'"
            message = "A new shop order has been receiveed."
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                notify_emails,
                reply_to=reply_to,
            )
            email.send()


@receiver(post_init, sender=BasketItem)
def post_init_item(sender, instance, **kwargs):
    # Remember current quantity on the instance
    instance._current_quantity = 0 if instance.pk is None else instance.quantity


@receiver(post_save, sender=BasketItem)
def post_save_item(sender, instance, **kwargs):
    quantity_diff = instance.quantity - instance._current_quantity
    if quantity_diff > 0:
        instance.product.stock -= quantity_diff
        instance.product.save()
    elif quantity_diff < 0:
        instance.product.stock += quantity_diff
        instance.product.save()


@receiver(post_delete, sender=BasketItem)
def post_delete_item(sender, instance, **kwargs):
    instance.product.stock += instance.quantity
    instance.product.save()

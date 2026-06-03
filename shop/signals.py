from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Transaction
from .csv_logger import log_transaction


def get_action_text(tx, incoming=False):
    if tx.tx_type == "BUY":
        product_name = tx.product.name if tx.product else "Unbekanntes Produkt"
        return f"BUY {product_name}"

    if tx.tx_type == "SEND":
        if incoming:
            return f"SEND_IN {tx.user.display_name}"
        recipient = tx.to_user.display_name if tx.to_user else "Unbekannt"
        return f"SEND_OUT {recipient}"

    return tx.tx_type


def get_signed_amount(tx, incoming=False, storno=False):

    amount = tx.amount

    if tx.tx_type == "SEND":
        base = -amount if not incoming else amount
    elif tx.tx_type == "BUY":
        base = -amount
    elif tx.tx_type == "TOPUP":
        base = amount
    elif tx.tx_type == "WITHDRAW":
        base = -amount
    else:
        base = amount

    if storno:
        base = -base

    return base


@receiver(pre_save, sender=Transaction)
def remember_old_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._was_canceled = False
        return

    try:
        old = Transaction.objects.get(pk=instance.pk)
        instance._was_canceled = old.canceled
    except Transaction.DoesNotExist:
        instance._was_canceled = False


@receiver(post_save, sender=Transaction)
def write_transaction_to_csv(sender, instance, created, **kwargs):


    if created:

        if instance.tx_type == "SEND":

            log_transaction(
                instance.user.display_name,
                get_action_text(instance, incoming=False),
                get_signed_amount(instance, incoming=False),
                instance.timestamp,
            )

            if instance.to_user:
                log_transaction(
                    instance.to_user.display_name,
                    get_action_text(instance, incoming=True),
                    get_signed_amount(instance, incoming=True),
                    instance.timestamp,
                )

        else:
            log_transaction(
                instance.user.display_name,
                get_action_text(instance),
                get_signed_amount(instance),
                instance.timestamp,
            )

        return

    if not instance._was_canceled and instance.canceled:

        if instance.tx_type == "SEND":

            log_transaction(
                instance.user.display_name,
                f"STORNO: {get_action_text(instance, incoming=False)}",
                get_signed_amount(instance, incoming=False, storno=True),
                instance.timestamp,
            )

            if instance.to_user:
                log_transaction(
                    instance.to_user.display_name,
                    f"STORNO: {get_action_text(instance, incoming=True)}",
                    get_signed_amount(instance, incoming=True, storno=True),
                    instance.timestamp,
                )

        else:
            log_transaction(
                instance.user.display_name,
                f"STORNO: {get_action_text(instance)}",
                get_signed_amount(instance, storno=True),
                instance.timestamp,
            )
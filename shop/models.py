from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    display_name = models.CharField(max_length=200)
    id12 = models.CharField(max_length=13, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.username} ({self.id12})"

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    id12 = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return f"{self.name} ({self.id12}) - {self.price}€"

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('BUY', 'User kauft Produkt'),
        ('TOPUP', 'User lädt Guthaben auf'),
        ('SEND', 'User schickt Geld zu anderem User'),
        ('WITHDRAW', 'User entnimmt Guthaben'),
    ]
    tx_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='incoming_transactions', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)
    canceled = models.BooleanField(default=False)

class AppSettings(models.Model):
    show_manage_menu = models.BooleanField(default=True, verbose_name="Show Management Menu")
    show_balance_in_user_list = models.BooleanField(default=True, verbose_name="Show Balance in User List")

class MagicId(models.Model):
    id12 = models.CharField(max_length=13, unique=True, verbose_name="Magic ID")
    target = models.CharField(max_length=255, verbose_name="Target")

class Meta:
    ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_tx_type_display()} {self.amount}€ ({self.timestamp})"
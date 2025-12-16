from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal

id12_validator = RegexValidator(regex=r'^\d{12}$', message='ID muss 12 Ziffern lang sein.')
id13_validator = RegexValidator(regex=r'^\d{13}$', message='ID muss 13 Ziffern lang sein.')

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    display_name = models.CharField(max_length=200)
    id12 = models.CharField(max_length=12, unique=True, validators=[id12_validator])
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.username} ({self.id12})"

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    id12 = models.CharField(max_length=13, unique=True, validators=[id13_validator])

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

class Meta:
    ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_tx_type_display()} {self.amount}€ ({self.timestamp})"
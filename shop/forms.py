from django import forms
from .models import User, Product

class TopUpForm(forms.Form):
    amount = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0.01)

class SendMoneyForm(forms.Form):
    to_user_id = forms.CharField(max_length=12)
    amount = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0.01)

class BuyByIdForm(forms.Form):
    product_id = forms.CharField(max_length=12)

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'display_name', 'id12', 'balance']

class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'id12']

class EditPriceForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['price']
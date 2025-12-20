from django import forms
from .models import User, Product

class TopUpForm(forms.Form):
    amount = forms.DecimalField(max_digits=8, decimal_places=2, min_value=0.01)

class SendMoneyForm(forms.Form):
    to_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Empfänger",
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label=None,
    )
    amount = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0.01,
        label="Betrag",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show "display_name (username)" in the select instead of the model's __str__
        self.fields['to_user'].label_from_instance = lambda u: f"{u.display_name} ({u.username})"

class BuyByIdForm(forms.Form):
    product_id = forms.CharField(max_length=13)

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
from django import forms
from .models import User, Product, MagicId

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
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Benutzername'}),
            'display_name': forms.TextInput(attrs={'size': 40, 'class': 'form-control', 'placeholder': 'Anzeigename'}),
            'id12': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID12'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Startguthaben in Euro', 'step': '0.01', 'min': '0.00'}),
        }

class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'id12']
        widgets = {
            'name': forms.TextInput(attrs={'size': 40, 'class': 'form-control', 'placeholder': 'Produktname'}),
            'id12': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID12'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preis in Euro', 'step': '0.01', 'min': '0.01'}),
        }

class EditPriceForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['price']

class CreateMagicIdForm(forms.ModelForm):
    class Meta:
        model = MagicId
        fields = ['id12', 'target']
        widgets = {
            'target': forms.TextInput(attrs={'size': 40, 'class': 'form-control', 'placeholder': 'Ziel der Magic ID'}),
            'id12': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Magic ID'}),
        }

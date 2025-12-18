from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db import transaction as db_transaction
from django.db.models import Q, Max
from django.contrib import messages
from decimal import Decimal
from django.http import JsonResponse
import random

from .models import User, Product, Transaction
from .forms import TopUpForm, SendMoneyForm, BuyByIdForm, CreateUserForm, CreateProductForm, EditPriceForm

ALLOWED_OVERDRAFT = Decimal('-25.00')

def index(request):
    q = request.GET.get('q', '').strip()
    users = User.objects.annotate(last_tx=Max('transactions__timestamp')).order_by('-last_tx')
    if request.method == 'POST':
        q = request.POST.get('q', '').strip()
        if q:
            try:
                user = User.objects.get(id12=q)
                return redirect('user_detail', id12=user.id12)
            except User.DoesNotExist:
                messages.error(request, 'Kein User mit dieser ID gefunden.')
    return render(request, 'shop/index.html', {'users': users, 'q': q})

def user_detail(request, id12):
    user = get_object_or_404(User, id12=id12)
    topup_form = TopUpForm()
    send_form = SendMoneyForm()
    buyid_form = BuyByIdForm()
    products = Product.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'topup':
            form = TopUpForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                with db_transaction.atomic():
                    user.balance += amount
                    user.save()
                    Transaction.objects.create(tx_type='TOPUP', amount=amount, user=user, note='Aufladung')
                messages.success(request, f'{amount}€ aufgeladen.')
            else:
                messages.error(request, 'Ungültiger Betrag.')
            return redirect('user_detail', id12=id12)

        elif action == 'topup_quick':
            try:
                amount = Decimal(request.POST.get('amount'))
            except Exception:
                messages.error(request, 'Ungültiger Betrag.')
                return redirect('user_detail', id12=id12)
            with db_transaction.atomic():
                user.balance += amount
                user.save()
                Transaction.objects.create(tx_type='TOPUP', amount=amount, user=user, note='Schnell-Aufladung')
            messages.success(request, f'{amount}€ aufgeladen.')
            return redirect('user_detail', id12=id12)

        elif action == 'buy':
            pid = request.POST.get('product_id')
            try:
                product = Product.objects.get(id12=pid)
            except Product.DoesNotExist:
                messages.error(request, 'Produkt nicht gefunden.')
                return redirect('user_detail', id12=id12)

            if user.balance - product.price < ALLOWED_OVERDRAFT:
                messages.error(request, 'Kauf würde Überziehungslimit überschreiten.')
                return redirect('user_detail', id12=id12)
            with db_transaction.atomic():
                user.balance -= product.price
                user.save()
                Transaction.objects.create(tx_type='BUY', amount=product.price, user=user, product=product)
            messages.success(request, f'Produkt {product.name} gekauft.')
            return redirect('user_detail', id12=id12)

        elif action == 'buy_by_id':
            form = BuyByIdForm(request.POST)
            if form.is_valid():
                pid = form.cleaned_data['product_id']
                try:
                    product = Product.objects.get(id12=pid)
                except Product.DoesNotExist:
                    messages.error(request, 'Produkt nicht gefunden.')
                    return redirect('user_detail', id12=id12)
                if user.balance - product.price < ALLOWED_OVERDRAFT:
                    messages.error(request, 'Kauf würde Überziehungslimit überschreiten.')
                    return redirect('user_detail', id12=id12)
                with db_transaction.atomic():
                    user.balance -= product.price
                    user.save()
                    Transaction.objects.create(tx_type='BUY', amount=product.price, user=user, product=product)
                messages.success(request, f'Produkt {product.name} gekauft.')
            else:
                messages.error(request, 'Ungültige Produkt-ID.')
            return redirect('user_detail', id12=id12)

        elif action == 'send':
            form = SendMoneyForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['to_user_username']
                amount = form.cleaned_data['amount']
                try:
                    to_user = User.objects.get(username=username)
                except User.DoesNotExist:
                    messages.error(request, 'Empfänger nicht gefunden.')
                    return redirect('user_detail', id12=id12)
                if user.balance - amount < ALLOWED_OVERDRAFT:
                    messages.error(request, 'Überziehungslimit würde überschritten.')
                    return redirect('user_detail', id12=id12)
                with db_transaction.atomic():
                    user.balance -= amount
                    to_user.balance += amount
                    user.save(); to_user.save()
                    Transaction.objects.create(tx_type='SEND', amount=amount, user=user, to_user=to_user)
                messages.success(request, f'{amount}€ an {to_user.display_name} gesendet.')
            else:
                messages.error(request, 'Ungültige Eingabe.')
            return redirect('user_detail', id12=id12)

        elif action == 'withdraw':
            try:
                amount = Decimal(request.POST.get('amount'))
            except Exception:
                messages.error(request, 'Ungültiger Betrag.')
                return redirect('user_detail', id12=id12)
            if user.balance - amount < ALLOWED_OVERDRAFT:
                messages.error(request, 'Überziehungslimit würde überschritten.')
                return redirect('user_detail', id12=id12)
            with db_transaction.atomic():
                user.balance -= amount
                user.save()
                Transaction.objects.create(tx_type='WITHDRAW', amount=amount, user=user)
            messages.success(request, f'{amount}€ entnommen.')
            return redirect('user_detail', id12=id12)

        elif action == 'undo_last':
            last = user.transactions.last()
            if not last:
                messages.error(request, 'Keine Transaktion zum Rückgängig machen.')
                return redirect('user_detail', id12=id12)
            with db_transaction.atomic():
                if last.tx_type == 'BUY':
                    user.balance += last.amount
                    user.save()
                elif last.tx_type == 'TOPUP':
                    user.balance -= last.amount
                    user.save()
                elif last.tx_type == 'SEND':
                    to_user = last.to_user
                    if to_user:
                        to_user.balance -= last.amount
                        to_user.save()
                    user.balance += last.amount
                    user.save()
                elif last.tx_type == 'WITHDRAW':
                    user.balance += last.amount
                    user.save()
                last.delete()
                messages.success(request, 'Letzte Transaktion rückgängig gemacht.')
            return redirect('user_detail', id12=id12)

    last_transactions = Transaction.objects.filter(Q(user=user) | Q(to_user=user)).order_by('-timestamp')[:10]
    context = {
        'user': user,
        'products': products,
        'last_transactions': last_transactions,
        'topup_form': topup_form,
        'send_form': send_form,
        'buyid_form': buyid_form,
    }
    return render(request, 'shop/user_detail.html', context)

def manage(request):
    users = User.objects.all().order_by('username')
    products = Product.objects.all().order_by('name')

    if request.method == 'POST':
        if 'create_user' in request.POST:
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'User erstellt.')
                return redirect('manage')
            else:
                messages.error(request, 'Fehler beim Erstellen des Users.')

        elif 'create_product' in request.POST:
            form = CreateProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Produkt erstellt.')
                return redirect('manage')
            else:
                messages.error(request, 'Fehler beim Erstellen des Produkts.')

        elif 'edit_price' in request.POST:
            pid = request.POST.get('product_pk')
            product = get_object_or_404(Product, pk=pid)
            form = EditPriceForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Preis geändert.')
                return redirect('manage')
            else:
                messages.error(request, 'Fehler beim Aktualisieren des Preises.')

    create_user_form = CreateUserForm()
    create_product_form = CreateProductForm()
    edit_price_form = EditPriceForm()
    return render(request, 'shop/manage.html', {
        'users': users,
        'products': products,
        'create_user_form': create_user_form,
        'create_product_form': create_product_form,
        'edit_price_form': edit_price_form,
    })
def generate_unique_id(request):
    while True:
        new_id = str(random.randint(10**11, 10**12 - 1))  # 12-stellig
        if not User.objects.filter(id12=new_id).exists() and not Product.objects.filter(id12=new_id).exists():
            return JsonResponse({"id": new_id})
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
import json as simplejson
import csv
import io

from main.models import Purse, Currency, Transaction

from django import forms


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/choose_purse')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


def choose_purse(request):
    if request.method == 'POST':
        if request.POST['purse_name']:
            purse = Purse()
            purse.name = request.POST['purse_name']
            purse.currency = Currency.objects.filter(name=request.POST['currency'])[0]
            purse.user = request.user
            purse.save()
        else:
            return redirect(f'/transactions/{Purse.get_purse_id(request.POST["purse"], request.user)}')

    args = {'currencies_names': Currency.names_list(),
            'purses_names': Purse.names_list(user=request.user)}
    return render(request, 'choose_purse.html', args)


# type(table): [{id, date, merchant, amount}]
def display_table(request, table: list):
    return render(request, 'display_table.html', {'tabledata':  simplejson.dumps(table)})


def transactions(request, purse_id):
    return display_table(request, Transaction.get_by_purse_id(purse_id))


def handle_csv_file(file, latest_id):
    transactions = file.read().decode('utf-8').split('\r\n')
    dict_list = []
    id = latest_id
    for transaction in transactions:
        id += 1
        fields = transaction.split(',')
        if len(fields) < 4:
            continue
        dict_list.append({'id': id,
                          'date': fields[0],
                          'merchant': fields[3],
                          'amount': fields[2]})
    return dict_list


def upload_transactions(request, purse_id):
    if request.method == 'POST':
        try:
            latest_id = Transaction.objects.filter(purse=purse_id).latest('id').id
        except:
            latest_id = 0

        dict_list = handle_csv_file(request.FILES['input_file'], latest_id)
        return display_table(request, dict_list)

    return render(request, 'upload_transactions.html')

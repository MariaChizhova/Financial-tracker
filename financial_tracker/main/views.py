from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
import json as simplejson
from django.core.files import File
import csv
import io

from django.views.decorators.csrf import csrf_exempt, csrf_protect

from main.models import Purse, Currency, Transaction, Category
from django.contrib.auth.models import User

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
    with open(f"data/categories/{request.user.id}.txt", "r") as file:
        dj_file = File(file)
        categories = []
        for line in dj_file:
            categories.append(line[:-1])

    return render(request, 'display_table.html', {'tabledata': simplejson.dumps(table), 'categories': categories})


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


def categories(request):
    data = []
    for c in Category.objects.filter(user=request.user):
        c_dict = {"id": str(c.id), "name": str(c.name), "parent": ""}
        if c.parent:
            c_dict["parent"] = str(c.parent.id)
        data.append(c_dict)

    if request.method == 'POST':

        # add category
        if 'new_category' in request.POST:
            if not request.POST['new_category']:
                return redirect('/categories')

            category = Category()
            category.user = request.user
            category.name = request.POST['new_category']

            if 'parent_category' in request.POST:
                category.parent = Category.objects.get(user=request.user,
                                                       name=request.POST['parent_category'])
            category.save()

        # edit category
        elif 'old_name' in request.POST:
            if not request.POST['old_name']:
                return redirect('/categories')

            if request.POST['new_name']:
                category = Category.objects.get(user=request.user,
                                                name=request.POST['old_name'])
                category.name = request.POST['new_name']
                category.save()

        # remove category
        elif 'remove_category' in request.POST:
            Category.objects.get(user=request.user,
                                 name=request.POST['remove_category']).delete()
        return redirect('/categories')

    return render(request, 'categories.html', {'data': data})


@csrf_exempt
def save_categories(request):
    print('sas')
    if request.is_ajax():
        if request.method == 'POST':
            with open(f"data/categories/{request.user.id}.txt", "wb") as file:
                dj_file = File(file)
                dj_file.write(request.body)
    return HttpResponse("OK")
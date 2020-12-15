import datetime
import time

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
import json as simplejson
from django.core.files import File

from django.views.decorators.csrf import csrf_exempt

from main.models import Purse, Currency, Transaction, Category
from decimal import Decimal


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
    args = {'purses': Purse.get_dict_id_name(user=request.user)}
    return render(request, 'choose_purse.html', args)


def create_purse(request):
    if request.method == 'POST':
        if request.POST['purse_name']:
            purse = Purse()
            purse.name = request.POST['purse_name']
            purse.currency = Currency.objects.filter(name=request.POST['currency'])[0]
            purse.user = request.user
            purse.save()
            return redirect(f'/transactions/{purse.id}')

    args = {'currencies_names': Currency.names_list()}
    return render(request, 'create_purse.html', args)


# type(table): [{id, date, merchant, amount}]
# def display_table(request, table: list):
def transactions_table(request, table: list):
    with open(f"data/categories/{request.user.id}.txt", "r") as file:
        dj_file = File(file)
        categories = []
        # for line in table:
        #     line['amount'] = float(line['amount'].strip(' ').strip('"'))
        for line in dj_file:
            categories.append({"label": line[:-1],
                               "value": line[:-1].replace('&ensp;', '')})

    # return render(request, 'display_table.html', {'tabledata': simplejson.dumps(table), 'categories': categories})
    return {'tabledata': simplejson.dumps(table), 'categories': categories}


# show transactions in purse
def transactions(request, purse_id):
    if request.method == 'POST':
        if 'upload_transactions' in request.POST:
            return redirect(f'/upload_transactions/{purse_id}')
        if 'edit_transactions' in request.POST:
            print("edit_transactions")
    sent_data = transactions_table(request, Transaction.get_by_purse_id(purse_id))
    sent_data['purse_name'] = Purse.objects.get(id=purse_id).name
    return render(request, 'display_table.html', sent_data)


def upload_transactions(request, purse_id):

    def handle_csv_file(file, latest_id, bank_name):
        def remove_quotes(s: str):
            return s.replace('"', '')

        def str_money_to_float(money: str):
            return float(money.replace(',', '.').replace('"', ''))

        def convert_date(date: str) -> str:
            print(date)
            date = remove_quotes(date)
            return date[-4:] + "-" + date[3:-5] + "-" + date[:2]

        if bank_name == 'tinkoff':
            col_num = {'date': 1, 'merchant': 11, 'amount': 4}
            character_set = 'cp1251'
            fields_sep = ';'

        elif bank_name == 'some_english_bank':
            col_num = {'date': 0, 'merchant': 3, 'amount': 2}
            character_set = 'utf-8'
            fields_sep = ','

        transactions = file.read().decode(character_set).split('\r\n')
        dict_list = []
        id = latest_id
        for transaction in transactions[1:]:
            id += 1
            fields = transaction.split(fields_sep)
            if len(fields) < 4:
                continue
            dict_list.append({'id': id,
                              'date': convert_date(fields[col_num['date']]),
                              'merchant': remove_quotes(fields[col_num['merchant']]),
                              'amount': str_money_to_float(fields[col_num['amount']])})
        return dict_list

    if request.method == 'POST':
        # Order: 3
        # save transactions to database
        if not request.FILES:
            Transaction.save_transactions(json_data=request.POST['saved_transactions'],
                                          purse_id=purse_id,
                                          user=request.user)

            return redirect(f'/transactions/{purse_id}')

        # Order: 2
        # read transactions from file
        try:
            latest_id = Transaction.objects.filter(purse=purse_id).latest('id').id
        except:
            latest_id = 0

        dict_list = handle_csv_file(request.FILES['input_file'], latest_id, request.POST['bank_name'])

        sent_data = transactions_table(request, dict_list)
        sent_data['purse_id'] = purse_id

        return render(request, 'save_transactions.html', sent_data)

    # Order: 1
    # get upload file form
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
    if request.is_ajax():
        if request.method == 'POST':
            with open(f"data/categories/{request.user.id}.txt", "wb") as file:
                dj_file = File(file)
                dj_file.write(request.body)
    return HttpResponse("OK")


def display_charts(request):
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    #queryset_categories = {'Food': [10500, 22456, 33454, 42355, 12543, 2134, 34534, 15437, 12345, 24351, 25160, 23610],
    #                       'Transport': [3234, 2344, 3454, 4566, 4883, 9362, 1234, 5430, 4235, 5423, 6463, 5466],
    #                       'Clothes': [1345, 3645, 3245, 6375, 3255, 4576, 2393, 5678, 4974, 3957, 5848, 9982],
    #                      'Medicine': [1038, 982, 1494, 973, 1245, 1774, 1948, 1737, 3773, 4948, 4345, 2734], }
    queryset_categories = Transaction.amount_in_year(user=request.user,
                                                     year=datetime.datetime.now().year)
    print(queryset_categories)
    total_sum = []
    for item in queryset_categories.values():
        val = round(sum(item), 2)
        if val >= 0:
            total_sum.append(round(sum(item), 2))
    #income = [10500, 22456, 33454, 42355, 12543, 2134, 34534, 15437, 12345, 24351, 25160, 23610]
    return render(request, 'display_charts.html', {'total_sum': total_sum,
                                                   'months': months, 'categories': categories,
                                                   'data': queryset_categories, 'income' : income})


def display_main(request):
    return render(request, 'display_main.html')

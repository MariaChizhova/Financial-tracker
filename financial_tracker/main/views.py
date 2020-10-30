from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
import json as simplejson

from main.models import Purse, Currency


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
            # TODO urls(/transactions/purse_id)

            return redirect(f'/transactions/{Purse.get_purse_id(request.POST["purse"], request.user)}')
    print(request.user)
    args = {'currencies_names': Currency.names_list(),
            'purses_names': Purse.names_list(user=request.user)}
    return render(request, 'choose_purse.html', args)


def display_table(request):
    List = [
        {'date': "05/09/1842", 'merchant': "APPLE.COM", 'amount': "20", 'category': "TECH"},
        {'date': "18/02/2000", 'merchant': "APPLE.COM", 'amount': "212", 'category': "TECH"},
        {'date': "23/05/1945", 'merchant': "YANDEX LAVKA", 'amount': "3", 'category': "FOOD"},
        {'date': "29/04/2011", 'merchant': "AMAZON.CO.UK", 'amount': "567", 'category': "-"},
        {'date': "29/04/2011", 'merchant': "METRO", 'amount': "8", 'category': "TRANSPORT"},
        {'date': "14/07/2020", 'merchant': "YANDEX TAXI", 'amount': "35", 'category': "TRANSPORT"},
        {'date': "01/06/2015", 'merchant': "BOLT", 'amount': "24.34", 'category': "TRANSPORT"},
        {'date': "02/07/2013", 'merchant': "SAMOKAT", 'amount': "34.11", 'category': "FOOD"},
        {'date': "01/06/2005", 'merchant': "GOOGLE", 'amount': "456", 'category': "-"},
        {'date': "18/10/1000", 'merchant': "GQT Wabash Landing 9", 'amount': "10", 'category': "CINEMA"},
    ]
    return render(request, 'display_table.html', {'tabledata':  simplejson.dumps(List)})

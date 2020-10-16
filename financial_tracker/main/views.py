from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

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


def get_currencies_names():
    names = []
    for c in Currency.objects.all():
        names.append(c.name)
    return names


# TODO maybe make get_model_names
def get_purses_names():
    names = []
    for c in Purse.objects.all():
        names.append(c.name)
    return names


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
            return redirect(f'/transactions/{Purse.objects.filter(name=request.POST["purse"])[0].id}')
    args = {'currencies_names': get_currencies_names(),
            'purses_names': get_purses_names()}
    return render(request, 'choose_purse.html', args)

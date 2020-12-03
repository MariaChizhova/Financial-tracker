from django.db import models
from django.contrib.auth.models import User
import datetime
import simplejson
from django.core.serializers.json import DjangoJSONEncoder


class Currency(models.Model):
    name = models.TextField()
    rate = models.FloatField()

    @staticmethod
    def names_list():
        names = []
        for c in Currency.objects.all():
            names.append(c.name)
        return names


class Purse(models.Model):
    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    @staticmethod
    def names_list(user):
        names = []
        for p in Purse.objects.filter(user=user):
            names.append(p.name)
        return names

    @staticmethod
    def get_purse_id(name, user):
        return Purse.objects.filter(name=name, user=user)[0].id


class Category(models.Model):
    name = models.TextField()
    name = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Transaction(models.Model):
    purse = models.ForeignKey(Purse, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    merchant = models.TextField()

    @staticmethod
    def get_by_purse_id(purse_id):
        query = Transaction.objects.filter(purse=purse_id)
        table = []
        for transaction in query:
            table.append({'id': transaction.id,
                          'date': str(transaction.date),
                          'merchant': transaction.merchant,
                          'category': transaction.category.name,
                          'amount': float(transaction.amount)})
        return table

    @staticmethod
    def save_transactions(json_data, purse_id, user):
        transactions_dict = simplejson.loads(json_data)

        for transaction in transactions_dict:
            if transaction['add_transaction'] and transaction['category']:
                print(transaction['date'][-4:] + "-" + transaction['date'][:2] + "-" + transaction['date'][3:-5])
                Transaction.objects.create(amount=transaction['amount'],
                                           merchant=transaction['merchant'],
                                           date=transaction['date'],
                                           category=Category.objects.get(user=user,
                                                                         name=transaction['category']),
                                           purse=Purse.objects.get(id=purse_id))

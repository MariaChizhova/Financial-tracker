from django.db import models
from django.contrib.auth.models import User
import datetime
import simplejson
import decimal
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
    def get_dict_id_name(user):
        result = {}
        for p in Purse.objects.filter(user=user):
            result[p.id] = p.name
        return result

    @staticmethod
    def get_purse_id(name, user):
        return Purse.objects.filter(name=name, user=user)[0].id


class Category(models.Model):
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

    # month: [1..12]
    # type(result): {category: amount}
    @staticmethod
    def amount_in_month(user, year, month):
        year = str(year)
        month = str(month)

        if len(month) == 1:
            month = '0' + month

        result = {}
        for category in Category.objects.filter(user=user):
            result[category.name] = 0

        # TODO: change to aggregate query
        query = Transaction.objects.filter(purse__user=user, date__year=year, date__month=month)

        for transaction in query:
            category_name = transaction.category.name
            amount = transaction.amount
            result[category_name] += amount

        for key, value in result.items():
            result[key] = float(value)

        return result

    # type(result): {category: [amount_in_month]}
    @staticmethod
    def amount_in_year(user, year):
        result = {}
        for month in range(1, 12 + 1):
            amount_in_month = Transaction.amount_in_month(user, year, month)
            for category, amount in amount_in_month.items():
                if category not in result:
                    result[category] = []
                result[category].append(amount)

        return result

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

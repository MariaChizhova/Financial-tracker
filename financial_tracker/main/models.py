from django.db import models
from django.contrib.auth.models import User


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
    parent = models.ForeignKey('self', on_delete=models.CASCADE)


class Transaction(models.Model):
    purse = models.ForeignKey(Purse, on_delete=models.CASCADE)
    amount = models.IntegerField()
    merchant = models.TextField()
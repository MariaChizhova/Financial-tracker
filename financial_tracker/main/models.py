from django.db import models
from django.contrib.auth.models import User


class Currency(models.Model):
    name = models.TextField()
    rate = models.FloatField()


class Purse(models.Model):
    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)


class Category(models.Model):
    name = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE)


class Transaction(models.Model):
    purse = models.ForeignKey(Purse, on_delete=models.CASCADE)
    amount = models.IntegerField()
    merchant = models.TextField()
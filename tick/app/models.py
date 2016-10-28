# coding: utf-8

from django.db import models


class Insider(models.Model):
    name = models.CharField(max_length=30, db_index=True)

    def __unicode__(self):
        return u'Insider {name}'.format(name=self.name)


class Company(models.Model):
    company_code = models.CharField(max_length=30, db_index=True)

    def __unicode__(self):
        return u'Company {code}'.format(code=self.company_code)

class InsTrade(models.Model):
    insider = models.ForeignKey('app.Insider', on_delete=models.CASCADE)
    company = models.ForeignKey('app.Company', on_delete=models.CASCADE)
    relation = models.CharField(max_length=40)
    date = models.DateField(db_index=True)
    transaction_type = models.CharField(max_length=40, default='')
    owner_type = models.CharField(max_length=40, default='')
    shares_traded = models.IntegerField(default=0)
    last_price = models.FloatField(default=0.0)
    shares_head = models.IntegerField(default=0)


class Trade(models.Model):
    company = models.ForeignKey('app.Company', on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    open_price = models.FloatField(default=0.0, db_index=True)
    high_price = models.FloatField(default=0.0, db_index=True)
    low_price = models.FloatField(default=0.0, db_index=True)
    close_price = models.FloatField(default=0.0, db_index=True)
    volume = models.IntegerField(default=0)

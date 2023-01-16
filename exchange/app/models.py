from djongo import models
from djongo.models.fields import ObjectIdField, Field
from django.contrib.auth.models import User
from decimal import Decimal

class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ips = models.Field(default=[])
    walletUserBTC = models.FloatField(default=0)
    walletUserValueBTC = models.FloatField(default=0)
    walletUserUSD = models.FloatField(default=0)
    def publish(self):
        self.save()

class Order(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    type = [
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),]
    orderType = models.CharField(max_length=10, choices=type, default='Buy')
    status = [('Open' , 'Open'),('Closed', 'Closed')]
    orderStatus = models.CharField(max_length=10, choices=status, default='Open')
    dateTime = models.DateTimeField(auto_now_add=True)
    priceOrder = models.FloatField(default=0)
    profitOrder = models.FloatField(default=0)
    quantity = models.FloatField(default=0)
    def createOrder(self):
        self.save()

class listTransaction(models.Model):
    _id = ObjectIdField()
    buyer = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name='buyer')
    buyerUser = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='buyeruser')
    price = models.FloatField(default=0)
    quantity = models.FloatField(default=0)
    seller = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name='seller')
    sellerUser = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='selleruser')
    def createList(self):
        self.save()
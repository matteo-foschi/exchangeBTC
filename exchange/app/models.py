from djongo import models
from djongo.models.fields import ObjectIdField, Field
from django.contrib.auth.models import User

class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ips = models.Field(default=[])
    walletUserBTC = models.FloatField(default=0)
    walletUserValueBTC = models.FloatField(default=0)
    walletUserUSD = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    def publish(self):
        self.save()

class Order(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    type = [
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),]
    OrderType = models.CharField(max_length=10, choices=type, default='Buy')
    status = [('Open' , 'Open'),('Closed', 'Closed')]
    OrderStatus = models.CharField(max_length=10, choices=status, default='Open')
    datetime = models.DateTimeField(auto_now_add=True)
    price_order = models.FloatField(default=None)
    price_end_order = models.FloatField(default=None)
    quantity = models.FloatField()
    def CreateOrder(self):
        self.save()

class listTransaction(models.Model):
    _id = ObjectIdField()
    buyer = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name='buyer')
    buyeruser = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='buyeruser')
    price = models.FloatField(default=None)
    quantity = models.FloatField(default=None)
    seller = models.ForeignKey(Profile, on_delete=models.DO_NOTHING, related_name='seller')
    selleruser = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='selleruser')
    def createList(self):
        self.save()
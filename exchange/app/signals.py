from django.db.models.signals import post_save
from django.contrib.auth.models import User
import random
from .models import Profile
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .cmc import CoinMarketCup

def customerProfile(sender, instance, created, **kwargs):
    if created:
        BTCEntry = random.randint(1, 10)
        data = CoinMarketCup()
        valueBTC = data.updated_data()
        Profile.objects.create(
            user=instance,
            walletUserBTC=BTCEntry,
            walletUserValueBTC=valueBTC*BTCEntry,
        )

post_save.connect(customerProfile, sender = User)

@receiver(user_logged_in)
def getIpAddress(sender, user, request, **kwargs):
    userIpAddress = request.META.get('HTTP_X_FORWARDED_FOR')
    if userIpAddress:
        ip = userIpAddress.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    Profile.objects.filter(user=user).update(ips=ip)
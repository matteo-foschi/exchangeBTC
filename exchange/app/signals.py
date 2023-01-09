from django.db.models.signals import post_save
from django.contrib.auth.models import User
import random
from .models import Profile
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .cmc import CoinMarketCup

def customer_profile(sender, instance, created, **kwargs):
    if created:
        BTCEntry = random.randint(1, 10)
        data = CoinMarketCup()
        ValueBTC = data.updated_data()
        Profile.objects.create(
            user=instance,
            walletUserBTC=BTCEntry,
            walletUserValueBTC=ValueBTC*BTCEntry,
        )

post_save.connect(customer_profile, sender = User)

@receiver(user_logged_in)
def get_ip_address(sender, user, request, **kwargs):
    user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if user_ip_address:
        ip = user_ip_address.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    Profile.objects.filter(user=user).update(ips=ip)
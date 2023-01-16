from django.contrib import admin
from django.urls import path, include
from app.views import registerPage, loginPage, exchangePage, logOutUser, buyOrder, openOrders, profitProfile, sellOrder

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', registerPage, name= "RegisterPage"),
    path('login/', loginPage, name= "LoginPage"),
    path('', exchangePage, name= "ExchangePage"),
    path('logout', logOutUser, name="logOutUser"),
    path('buyorder/', buyOrder, name="buyOrder"),
    path('sellorder/', sellOrder, name="sellOrder"),
    path('openorders/', openOrders, name="OpenOrders"),
    path('profitprofile/', profitProfile, name="profitProfile"),
]

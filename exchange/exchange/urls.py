from django.contrib import admin
from django.urls import path, include
from app.views import registerPage, loginPage, exchangePage, logOutUser, create_order, OpenOrders, profitProfile, sell_order

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', registerPage, name= "RegisterPage"),
    path('login/', loginPage, name= "LoginPage"),
    path('', exchangePage, name= "ExchangePage"),
    path('logout', logOutUser, name="logOutUser"),
    path('buyorder/', create_order, name="buyOrder"),
    path('sellorder/', sell_order, name="sellOrder"),
    path('openorders/', OpenOrders, name="OpenOrders"),
    path('profitprofile/', profitProfile, name="profitProfile"),
]

from django.contrib.auth import authenticate, login, logout
from .models import Profile, Order
from django.shortcuts import render, redirect
from .form import CreateUserForm, OrderForm
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from .cmc import CoinMarketCup
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


def exchangePage(request):
    if request.user.is_authenticated:
        UserDataProfile = Profile.objects.get(user=request.user)
        context = {'userData':UserDataProfile}
    else:
        context = {}
    return render(request, 'account/exchange.html', context)


def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('LoginPage')
        else:
            messages.error(request, 'Registration not completed, Please check the typed information. The user could be exsiting or you forgot to insert all the data required.')

    context = {'form':form}
    return render(request, 'account/register.html', context)

def loginPage(request):
    # if request.user.is_authenticated:
        # return redirect('ExchangePage')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('ExchangePage')
        else:
            messages.info(request, 'Username Or Password is incorrect')
    context = {}
    return render(request, 'account/login.html', context)


def logOutUser(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('LoginPage')


def create_order(request):
    form = OrderForm()
    orderMatch = False
    if request.method == 'POST':
        form = OrderForm(request.POST)
        orderCreated = Order()
        if form.is_valid():
            Buyer = Profile.objects.get(user=request.user)
            price = form.cleaned_data.get('price')
            quantity = form.cleaned_data.get('quantity')
            #If the buyer don't have USD in Wallet he can't buy other BTC
            if Buyer.walletUserUSD < form.cleaned_data.get('price'):
                messages.info(request, "You USD balance is not enough for Sell order")
                return redirect('buyOrder')
            else:
                orderCreated.profile = request.user
                orderCreated.OrderType = 'Buy'
                orderCreated.datetime = datetime.now()

                orderCreated.price_order = form.cleaned_data.get('price')
                orderCreated.quantity = form.cleaned_data.get('quantity')

                orderCreated.price_end_order = 0

                #Filter the first Sell order published by a different Profile, ordered by date, with status Open and with the same quantity and the price in grather or equal than the sell price.

                order_price = Order.objects.filter(OrderType='Sell', OrderStatus='Open', price_order__lte=price, quantity__gte=quantity).order_by('-quantity', 'price_order', 'datetime').first()

                print(order_price)
                #If I found an order that respect the filter i close the new order and the order found

                if order_price is not None:
                    #Set the sell order closed end and the price equal the buy price
                    order_price.OrderStatus = 'Closed'
                    order_price.price_end_order = price
                    order_price.save()

                    print(order_price)
                    #Set the buy order closed and the price equale the buy price
                    orderCreated.price_end_order = price
                    orderCreated.OrderStatus = 'Closed'
                    print(order_price.profile)
                    #I increase the profile for the costumer of the Sell order
                    #object_id = ObjectId('63b447c1292b464c9780a09c')
                    object_id = order_price.profile
                    object_id = str(object_id)
                    print(object_id)
                    sellCustomer = Profile.objects.get(user=order_price.profile)
                    print(sellCustomer)

                    sellCustomer.walletUserUSD = sellCustomer.walletUserUSD + price
                    sellCustomer.save()
                    Buyer.walletUserBTC = Buyer.walletUserBTC + quantity

                    orderMatch = True

                else:
                    orderCreated.OrderStatus = 'Open'
                #I decrease the profile for the buyer

                Buyer.walletUserUSD = Buyer.walletUserUSD - price
                Buyer.save()

                orderCreated.CreateOrder()
                if orderMatch is True:
                    messages.success(request, 'Buy order correctly published for: ' + str(quantity) + ' BTC at the price: ' + str(price) + ' USD and sucessfully selled' )
                else:
                    messages.success(request, 'Buy order correctly published for: ' + str(quantity) + ' BTC at the price: ' + str(price) + ' USD')
                return redirect('ExchangePage')
        else:
            messages.info(request, "Information in the form is not valid")


    context = {'form': form}
    return render(request, 'account/buyOrder.html', context)


def sell_order(request):
    form = OrderForm()
    orderMatch = False
    if request.method == 'POST':
        form = OrderForm(request.POST)
        orderCreated = Order()
        if form.is_valid():
            Seller = Profile.objects.get(user=request.user)
            price = form.cleaned_data.get('price')
            quantity = form.cleaned_data.get('quantity')
            #If the buyer don't have USD in Wallet he can't buy other BTC
            if Seller.walletUserBTC < form.cleaned_data.get('quantity'):
                messages.info(request, "You BTC balance is not enough for Buy order")
                return redirect('sellOrder')
            else:
                orderCreated.profile = request.user
                orderCreated.OrderType = 'Sell'
                orderCreated.datetime = datetime.now()

                orderCreated.price_order = form.cleaned_data.get('price')
                orderCreated.quantity = form.cleaned_data.get('quantity')

                orderCreated.price_end_order = 0

                #Filter the first Sell order published by a different Profile, ordered by date, with status Open and with the same quantity and the price in grather or equal than the sell price.

                order_price = Order.objects.filter(OrderType='Buy', OrderStatus='Open', price_order__gte=price, quantity__lte=quantity).order_by('-quantity', 'price_order', 'datetime').first()

                print(order_price)
                #If I found an order that respect the filter i close the new order and the order found

                if order_price is not None:
                    #Set the sell order closed end and the price equal the buy price
                    order_price.OrderStatus = 'Closed'
                    order_price.price_end_order = price
                    order_price.save()

                    #Set the buy order closed and the price equale the buy price
                    orderCreated.price_end_order = price
                    orderCreated.OrderStatus = 'Closed'

                    #I increase the profile for the costumer of the Sell order

                    BuyCustomer = Profile.objects.get(user=order_price.profile)

                    BuyCustomer.walletUserBTC = BuyCustomer.walletUserBTC + quantity
                    BuyCustomer.save()
                    Seller.walletUserUSD = Seller.walletUserUSD + quantity
                    orderMatch = True
                else:
                    orderCreated.OrderStatus = 'Open'
                #I decrease the profile for the buyer

                Seller.walletUserBTC = Seller.walletUserBTC - quantity
                Seller.save()

                orderCreated.CreateOrder()
                if orderMatch is True:
                    messages.success(request, 'Sell order correctly published for: ' + str(quantity) + ' BTC at the price: ' + str(price) + ' USD and sucessfully buyed' )
                else:
                    messages.success(request, 'Sell order correctly published for: ' + str(quantity) + ' BTC at the price: ' + str(price) + ' USD')
                return redirect('ExchangePage')
        else:
            messages.info(request, "Information in the form is not valid")
    context = {'form': form}
    return render(request, 'account/sellOrder.html', context)

def OpenOrders(request):
    response = []
    results = Order.objects.filter(OrderStatus='Open').order_by('datetime')
    for r in results:
        response.append(
            {
                "id_order" : r.id,
                "profile" : str(r.profile),
                "OrderType" : r.OrderType,
                "OrderStatus" : r.OrderStatus,
                "datetime" : r.datetime,
                "price_order" : r.price_order,
                "quantity" : r.quantity,
            }
        )
    return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})

@staff_member_required
def profitProfile(request):
    response = []
    data = CoinMarketCup()
    UserPendingBuy = 0
    UserPendingSell = 0
    userProfile = Profile.objects.filter()
    for r in userProfile:
        userAmmount = (r.walletUserBTC * data.updated_data()) + r.walletUserUSD
        print('utente ' + str(r.user))
        print('BTC in portafoglio ' + str(r.walletUserBTC))
        print('prezzo BTC: ' + str(data.updated_data()))
        print('Wallet USD' + str(r.walletUserUSD))
        print('Totale: ' + str(userAmmount))
        orderPendingBuy = Order.objects.filter(profile=r.user, OrderStatus='Open', OrderType='Buy')
        for order in orderPendingBuy:
            UserPendingBuy = UserPendingBuy + order.price_order

        print(UserPendingBuy)
        orderPendingSell = Order.objects.filter(profile=r.user, OrderStatus='Open', OrderType='Sell')
        for order in orderPendingSell:
            UserPendingSell = UserPendingSell + (order.quantity * data.updated_data())
        print(UserPendingSell)
        print(r.walletUserValueBTC)
        profit = userAmmount + UserPendingBuy + UserPendingSell - r.walletUserValueBTC
        print(profit)
        response.append(
            {
                "profile": str(r._id),
                "User": str(r.user),
                "Profit": profit,
            }
        )
    return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})

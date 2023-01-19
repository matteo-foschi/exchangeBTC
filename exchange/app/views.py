from django.contrib.auth import authenticate, login, logout
from .models import Profile, Order
from django.shortcuts import render, redirect
from .form import CreateUserForm, OrderForm
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from .cmc import CoinMarketCup
import pymongo
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from decimal import Decimal

def exchangePage(request):
    if request.user.is_authenticated:
        UserDataProfile = Profile.objects.get(user=request.user)
        context = {'userData': UserDataProfile}
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

def buyOrder(request):
    form = OrderForm()
    orderMatch = False
    if request.method == 'POST':
        form = OrderForm(request.POST)
        orderCreated = Order()

        if form.is_valid():
            user = request.user
            buyer = Profile.objects.get(user=request.user)
            price = form.cleaned_data.get('price')
            quantity = form.cleaned_data.get('quantity')
            totalPriceBuy = price * quantity
            #If the buyer don't have USD in Wallet he can't buy other BTC
            if buyer.walletUserUSD < totalPriceBuy:
                messages.info(request, "You USD balance is not enough for buy order.")
                return redirect('buyOrder')
            else:
                orderFindMatch = True
                orderCreated.profile = request.user
                orderCreated.orderType = 'Buy'
                orderCreated.dateTime = datetime.now()
                orderCreated.priceOrder = form.cleaned_data.get('price')

                #While Cylce thath check for all the Sell open orders order by price and date, that match with the order price
                while orderFindMatch:
                    orderFinded = Order.objects.filter(~Q(profile=user), orderType='Sell', orderStatus='Open', priceOrder__lte=price).order_by('priceOrder', 'dateTime').first()

                    if orderFinded is not None:
                        orderMatch = True
                        quantityTransaction = 0
                        #I check the Profile related to the Sell order found
                        sellCustomer = Profile.objects.get(user=orderFinded.profile)

                        if quantity >= orderFinded.quantity:
                            #Increased the BTC Wallet of the buyer and USD Wallet for the seller
                            buyer.walletUserBTC = buyer.walletUserBTC + orderFinded.quantity
                            sellCustomer.walletUserUSD = sellCustomer.walletUserUSD + (price*orderFinded.quantity)

                            print(sellCustomer.walletUserUSD)
                            print(price*orderFinded.quantity)
                            print(sellCustomer.walletUserUSD)

                            sellCustomer.save()
                            #Decresed the Buyers Wallet USD by the amount of the price/quantity that match with the Sell order
                            buyer.walletUserUSD = buyer.walletUserUSD - (price * orderFinded.quantity)
                            #The new quantity for this Buy order will be decreased by the quantity of the sell order closed
                            quantityTransaction = orderFinded.quantity
                            quantity = quantity - orderFinded.quantity
                            #Calculation of the profit for Sell order
                            print(price - orderFinded.priceOrder)
                            print(quantityTransaction)
                            orderFinded.profitOrder = orderFinded.profitOrder + ((price - orderFinded.priceOrder) * quantityTransaction)
                            #The quantity of Sell order was used in total, then put the quantity for the order to 0
                            orderFinded.quantity = 0
                            orderFinded.save()
                            print('Buy con quantità maggiore dell ordine di vendita')
                        else:
                            #Increased the BTC Wallet of the buyer and USD Wallet for the seller
                            buyer.walletUserBTC = buyer.walletUserBTC + quantity
                            sellCustomer.walletUserUSD = sellCustomer.walletUserUSD + (price * quantity)
                            sellCustomer.save()
                            #Decresed the Buyers Wallet USD by the amount of the price/quantity that match with the Sell order
                            buyer.walletUserUSD = buyer.walletUserUSD - (price * quantity)
                            #Calculation of the profit for Sell order
                            orderFinded.profitOrder = orderFinded.profitOrder + ((price - orderFinded.priceOrder) * quantity)
                            x = Decimal(orderFinded.quantity) - Decimal(quantity)
                            y = float(x)
                            #The buy quantity is less then the Sell quantity, then I can't close the Sell order and reduce the Sell quantity by Buy quantity
                            orderFinded.quantity = y
                            orderFinded.save()
                            quantityTransaction = quantity
                            quantity = 0
                            print('Buy con quantità minore dell ordine di vendita')
                        #If sell order fined have quantity equal to 0, close the Sell order
                        if orderFinded.quantity == 0:
                            orderFinded.orderStatus = 'Closed'
                            orderFinded.save()

                        #Save the transaction in a transaction list database
                        personalClientMdb = pymongo.MongoClient("mongodb://localhost:27017/")
                        transactionDocument = personalClientMdb.get_database("exchange-db")
                        transactionList = transactionDocument['Transactions Closed List']
                        saveTransactionClosed = {
                            'Buy User': str(buyer.user),
                            'Buy Profile': str(buyer._id),
                            'Order Type': 'Buy',
                            'BTC Quantity': quantityTransaction,
                            'Price Buy': price,
                            'Sell Order Price': str(orderFinded.priceOrder),
                            'Sell User': str(sellCustomer.user),
                            'Sell Profile': str(sellCustomer._id),
                            'Seller Profit Order': str(orderFinded.profitOrder),
                        }
                        save_transaction = transactionList.insert_one(saveTransactionClosed)
                    else:
                        #If there are no order match the Buy order is in Open status for the remain quantity
                        orderCreated.orderStatus = 'Open'
                        buyer.walletUserUSD = buyer.walletUserUSD - (price * quantity)
                        if quantity == 0:
                            orderCreated.orderStatus = 'Closed'
                        orderFindMatch = False
                    if quantity == 0:
                        orderCreated.orderStatus = 'Closed'
                        orderFindMatch = False

                #Save buy profile  after all the controls
                buyer.save()
                #Save the Buy order created
                orderCreated.quantity = quantity
                orderCreated.createOrder()

                if orderMatch is True:
                    messages.success(request, 'Buy order correctly published' )
                else:
                    messages.success(request, 'Buy order correctly published for: ' + str(quantity) + ' BTC at the price: ' + str(price) + ' USD in waiting open orders list')
                return redirect('ExchangePage')
        else:
            messages.info(request, "Information in the form is not valid")
    context = {'form': form}
    return render(request, 'account/buyOrder.html', context)

def sellOrder (request):
    form = OrderForm()
    orderMatch = False
    if request.method == 'POST':
        form = OrderForm(request.POST)
        orderCreated = Order()

        if form.is_valid():
            user = request.user
            seller = Profile.objects.get(user=request.user)
            price = form.cleaned_data.get('price')
            quantity = form.cleaned_data.get('quantity')
            #If the seller don't have BTC in Wallet he can't buy other BTC
            if seller.walletUserBTC < quantity:
                messages.info(request, "You BTC balance is not enough for sell order.")
                return redirect('sellOrder')
            else:
                orderFindMatch = True
                orderCreated.profile = request.user
                orderCreated.orderType = 'Sell'
                orderCreated.dateTime = datetime.now()
                orderCreated.priceOrder = form.cleaned_data.get('price')

                #While Cylce thath check for all the Buy open orders order by price and date, that match with the order price
                while orderFindMatch:
                    orderFinded = Order.objects.filter(~Q(profile=user), orderType='Buy', orderStatus='Open', priceOrder__gte=price).order_by('priceOrder', 'dateTime').first()

                    if orderFinded is not None:
                        orderMatch = True
                        quantityTransaction = 0
                        #I check the Profile related to the Buy order found
                        buyerCustomer = Profile.objects.get(user=orderFinded.profile)

                        if quantity >= orderFinded.quantity:
                            #Increased the USD Wallet of the seller and BTC Wallet for the buyer
                            seller.walletUserUSD = seller.walletUserUSD + (orderFinded.quantity*orderFinded.priceOrder)
                            buyerCustomer.walletUserBTC = buyerCustomer.walletUserBTC + orderFinded.quantity
                            buyerCustomer.save()
                            #Decresed the seller Wallet BTC by the amount of the price/quantity that match with the buy order
                            seller.walletUserBTC = seller.walletUserBTC - orderFinded.quantity
                            #The new quantity for this sell order will be decreased by the quantity of the buy order closed
                            quantityTransaction = orderFinded.quantity
                            quantity = quantity - orderFinded.quantity
                            #Calculation of the profit for Sell order
                            orderCreated.profitOrder = (orderFinded.priceOrder - price) * orderFinded.quantity
                            #The quantity of Sell order was used in total, then put the quantity for the order to 0
                            orderFinded.quantity = 0
                            orderFinded.save()
                        else:
                            #Increased the USD Wallet of the seller and BTC Wallet for the buyer
                            seller.walletUserUSD = seller.walletUserUSD + (quantity*orderFinded.priceOrder)
                            buyerCustomer.walletUserBTC = buyerCustomer.walletUserBTC + quantity
                            buyerCustomer.save()
                            #Decresed the seller Wallet BTC by the amount of the price/quantity that match with the buy order
                            seller.walletUserBTC = seller.walletUserBTC - quantity
                            #Calculation of the profit for Sell order
                            orderCreated.profitOrder = orderCreated.profitOrder + (orderFinded.priceOrder - price) * quantity
                            x = Decimal(orderFinded.quantity) - Decimal(quantity)
                            y = float(x)
                            #The buy quantity is less then the buy quantity, then I can't close the sell order and reduce the buy quantity by sell quantity
                            orderFinded.quantity = y
                            orderFinded.save()
                            quantityTransaction = quantity
                            quantity = 0
                        #If buy order fined have quantity equal to 0, close the buy order
                        if orderFinded.quantity == 0:
                            orderFinded.orderStatus = 'Closed'
                            orderFinded.save()

                        #Save the transaction in a transaction list database
                        personalClientMdb = pymongo.MongoClient("mongodb://localhost:27017/")
                        transactionDocument = personalClientMdb.get_database("exchange-db")
                        transactionList = transactionDocument['Transactions Closed List']
                        saveTransactionClosed = {
                            'Sell User': str(seller.user),
                            'Sell Profile': str(seller._id),
                            'Order Type': 'Buy',
                            'BTC Quantity': quantityTransaction,
                            'Price Sell': price,
                            'Buy Order Price': str(orderFinded.priceOrder),
                            'Buy User': str(buyerCustomer.user),
                            'Buy Profile': str(buyerCustomer._id),
                            'Seller Profit Order': str(orderCreated.profitOrder),
                        }
                        save_transaction = transactionList.insert_one(saveTransactionClosed)
                    else:
                        #If there are no order match the sell order is in Open status for the remain quantity
                        orderCreated.orderStatus = 'Open'
                        seller.walletUserBTC = seller.walletUserBTC - quantity
                        if quantity == 0:
                            orderCreated.orderStatus = 'Closed'
                        orderFindMatch = False
                    if quantity == 0:
                        orderCreated.orderStatus = 'Closed'
                        orderFindMatch = False

                #Save seller profile  after all the controls
                seller.save()
                #Save the Sell order created
                orderCreated.quantity = quantity
                orderCreated.createOrder()

                if orderMatch is True:
                    messages.success(request, 'Sell order correctly published' )
                else:
                    messages.success(request, 'Sell order correctly published for: ' + str(quantity) + ' BTC at the price: ' + str(price) + ' USD in waiting open orders list')
                return redirect('ExchangePage')
        else:
            messages.info(request, "Information in the form is not valid")
    context = {'form': form}
    return render(request, 'account/sellOrder.html', context)

def openOrders(request):
    response = []
    results = Order.objects.filter(orderStatus='Open').order_by('dateTime')
    for r in results:
        response.append(
            {
                "id_order": r.id,
                "profile": str(r.profile),
                "orderType": r.orderType,
                "orderStatus": r.orderStatus,
                "dateTime": r.dateTime,
                "priceOrder": r.priceOrder,
                "quantity": r.quantity,
            }
        )
    return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})

@staff_member_required
def profitProfile(request):
    response = []
    data = CoinMarketCup()
    userProfile = Profile.objects.filter()
    for r in userProfile:
        userPendingBuy = 0
        userPendingSell = 0
        userAmmount = (r.walletUserBTC * data.updated_data()) + r.walletUserUSD

        orderPendingBuy = Order.objects.filter(profile=r.user, orderStatus='Open', orderType='Buy')
        for order in orderPendingBuy:
            userPendingBuy = userPendingBuy + (order.priceOrder * order.quantity)

        orderPendingSell = Order.objects.filter(profile=r.user, orderStatus='Open', orderType='Sell')
        for order in orderPendingSell:
            userPendingSell = userPendingSell + (order.priceOrder * order.quantity)

        profit = userAmmount + userPendingBuy + userPendingSell - r.walletUserValueBTC
        response.append(
            {
                "profile": str(r._id),
                "User": str(r.user),
                "Profit": profit,
            }
        )
    return JsonResponse(response, safe=False, json_dumps_params={'indent': 3})

from django.shortcuts import render
from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from forex_python.converter import CurrencyCodes, CurrencyRates
from forex_python.bitcoin import BtcConverter
import uuid
# from .forms import AgentUploadFileForm, AgentSignUpForm, ProfileUploadForm, ImageForm
import os 
# from django.template import loader
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from main.models import Invest, Invest_plan, InvestmentModel, Message, Payment_Method, Referral, WithdrawModel
from .token_generator import account_activation_token
# from PIL import Image
from functools import wraps
from datetime import datetime, timedelta



def wrappers(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped

def staff_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            property("admin here")
            return f(request, *args, **kwargs)
        return render(request, 'no_access.html', {'media_url': settings.MEDIA_URL, 'media_root': settings.MEDIA_ROOT,})
        

    return wrap



def is_logged_in(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated == True:
            return redirect('main:dashboard')
        else:
           
            return f(request, *args, *kwargs)

    return wrap

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true
        user.is_active = True
        profile = user.profile # because of signal and one2one relation
        profile.email_confirm = True
        profile.save()
        # set signup_confirmation true

        user.save()
        
        

        messages.add_message(request, messages.SUCCESS, 'email authenticated')
        return redirect('main:login')
    else:
        messages.add_message(request, messages.WARNING, 'iNVALID LINK or EXPIRED')
        return redirect('/')

def resend(request, username):

    user = User.objects.get(email=username)
    try:
        current_site = get_current_site(request)
        email_subject = 'Activate Your Capitalcointradefx Account'
        message = render_to_string('activate_account.html', {
                'user': user.username,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': account_activation_token.make_token(user),
            })
        to_email = user.email
        email = EmailMessage(email_subject, message, to=[to_email])
        email.content_subtype = 'html'
        email.send()
        messages.add_message(request, messages.SUCCESS, f'Email has been sent to {user.email}, check your email')
    except:
        messages.add_message(request, messages.ERROR, 'Something Went wrong try again...')
        return redirect('main:login')
    
    # print('pomit', User.objects.get(username=username).profile.email_confirm)
    
    return redirect('main:login')

@csrf_exempt
def ContactUs(request):
    name = request.POST.get('name', None)
    phone = request.POST.get('phone', None)
    email = request.POST.get('email', None)
    message = request.POST.get('message', None)
    print(email, message)

    email_subject = f'{name} Just contacted you'
    message = render_to_string('contactemail.html', {
            'name': name,
            'phone': phone,
            'email': email,
            'message': message,
        })
    to_email = 'capitalcointradefx@gmail.com'
    email = EmailMessage(email_subject, message, to=[to_email])
    email.content_subtype = 'html'
    email.send()
    messages.add_message(request, messages.SUCCESS, 'Thank you for contacting us, we would get back to you soon')


    # try:
    #     current_site = get_current_site(request)
    #     email_subject = f'{name} Just contacted you'
    #     message = render_to_string('contactemail.html', {
    #             'name': name,
    #             'phone': phone,
    #             'email': email,
    #             'message': message,
    #         })
    #     to_email = email
    #     email = EmailMessage(email_subject, message, to=[to_email])
    #     email.content_subtype = 'html'
    #     email.send()
    #     messages.add_message(request, messages.SUCCESS, 'Thank you for contacting us, we would get back to you soon')

        
    # except:
    #     messages.add_message(request, messages.ERROR, 'Something Went wrong try again...')
        
    

    
    return JsonResponse({'message':'username Does not exist', 'message_type':'danger'})
    



def  Home(request):
    invest = Invest_plan.objects.all()
    lastInvest = InvestmentModel.objects.filter(confirm=True).order_by('-date')[:8]
    return render(request, 'index.html', {'media_url': settings.MEDIA_URL, 'invest': invest, 'stat':lastInvest})

@is_logged_in
@csrf_exempt
def  Login(request):
    
    if request.method == 'POST':
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        
        

        
        print(email, password,)
        
        if not User.objects.filter(email=email).exists():
            return JsonResponse({'message':'email Does not exist', 'message_type':'danger'})
        username = User.objects.get(email=email).username
        if not authenticate(username=username, password=password):
            return JsonResponse({'message':'password does not match', 'message_type':'warning'})

        if User.objects.get(username=username).profile.email_confirm is False:
            resend = reverse('main:resend', kwargs={'username':email})
            print(resend)
            print(User.objects.get(username=username).profile.email_confirm)
            return JsonResponse({'message': f'Email is not verified. click <a href="{resend}" style="color: blue;">here</a> to resend, if you have not recieved email-verification email...', 'message_type':'danger'})

        user = authenticate(username=username, password=password)

        login(request, user)
        request.session['username'] = username
        # if request.user.profile.role ==  'Agent':
        #     return JsonResponse({'success':'success',
        #     'redirect': reverse('main:register'),})

        return JsonResponse({'message':'success', 'redirect': reverse('main:dashboard'), 'message_type':'success'})

        # load1 = request.POST.get('load1', None)
    return render(request, 'login.html', {'media_url': settings.MEDIA_URL, 'media_root': settings.MEDIA_ROOT,})

@is_logged_in
@csrf_exempt
def Register(request):
    ref = request.GET.get('referral')
    print(ref)
    if request.method == 'POST':


        firstname = request.POST.get('name', None)
        lastname = request.POST.get('lastname', None)
        username = request.POST.get('username', None)
        emaill = request.POST.get('email', None)
        password1 = request.POST.get('password', None)
        password2 = request.POST.get('password2', None)
        phone = request.POST.get('phone', None)
        ref = request.POST.get('ref', None)
        print(firstname, lastname, username, emaill, password1, password2, phone, ref)

        
        
        if User.objects.filter(username=username).exists():
            print('1 vv')
            return JsonResponse({'message':'username already exists', 'message_type':'danger'})

        if User.objects.filter(email=emaill).exists():
            print('2 vv')
            return JsonResponse({'message':'email already in use','message_type':'danger'})

        if len(password1) < 5:
            print('3 vv')
            return JsonResponse({'message':'password should be greater than 5', 'message_type':'warning'})
        user = User.objects.create(
            first_name = firstname,
            last_name = lastname,
            username = username,
            email = emaill,
            password = make_password(password1),
        )

        try:
            current_site = get_current_site(request)
            email_subject = 'Activate Your Capitalcointradefx Account'
            message = render_to_string('activate_account.html', {
                    'user': user.username,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.id)),
                    'token': account_activation_token.make_token(user),
                })
            to_email = emaill
            email = EmailMessage(email_subject, message, to=[to_email])
            email.content_subtype = 'html'
            email.send()
        except:
            User.objects.filter(pk=user.id).delete()
            return JsonResponse({'message':'Something went wrong- your email address might not be valid', 'message_type':'danger'})


        user =  User.objects.get(username=username,)
        profile = user.profile # because of signal and one2one relation
        # profile.phone = phone
        profile.save()

        if User.objects.filter(username=ref).exists():
            Ruser =  User.objects.get(username=ref)
            Referral.objects.create(
                ref = Ruser,
                ref_user = user
            )
        messages.add_message(request, messages.SUCCESS, 'Successfully created account, confirm email to login')

        return JsonResponse({'message':'Succesfully created your account', 'redirect': reverse('main:login'), 'message_type':'success'})
    return render(request, 'register.html', {'media_url': settings.MEDIA_URL, 'media_root': settings.MEDIA_ROOT, 'ref': ref,})

@login_required(login_url='/Login')
def  Dashboard(request):
    current_site = get_current_site(request)
    invest = Invest_plan.objects.all()
    user= request.user
    print(User._meta.get_fields(), user.profile.phone)
    return render(request, 'dashboard.html', {'media_url': settings.MEDIA_URL, 'invest': invest,'domain': current_site.domain,})

def  About(request):
    return render(request, 'about.html', {'media_url': settings.MEDIA_URL, 'media_root': settings.MEDIA_ROOT,})

def  contact(request):
    return render(request, 'contact.html', {'media_url': settings.MEDIA_URL, 'media_root': settings.MEDIA_ROOT,})


@login_required(login_url='/Login')
def  Investments(request):
    invest = Invest_plan.objects.all()
    pay = Payment_Method.objects.all()
    return render(request, 'invest.html', {'media_url': settings.MEDIA_URL, 'invest': invest, 'pay': pay,})

@login_required(login_url='/Login')
@csrf_exempt
def  Funds(request):
    invest = Invest_plan.objects.all()
    pay = Payment_Method.objects.all()
    random = str(uuid.uuid4().hex)[:12]
    if request.method == 'POST':
        username = request.POST.get('username', None)
        amount = request.POST.get('amount', None)
        method1 = request.POST.get('method', None)
        des = request.POST.get('des', None)
        trx = request.POST.get('trx', None)

        try:
            current_site = get_current_site(request)
            email_subject = f'{username} Just Requested withdrawal'
            message = render_to_string('requestemail.html', {
                    'username': username,
                    'amount': amount,
                    'method': method1,
                    'des': des,
                    
                })
            to_email = 'capitalcointradefx@gmail.com'
            email = EmailMessage(email_subject, message, to=[to_email])
            email.content_subtype = 'html'
            email.send()

            # Send message to user
            emailto = User.objects.get(username=username)
            email_subject1 = f'Your request has been received'
            message1 = render_to_string('requestfunds.html', {
                    'user': emailto,
                    'amount': amount,
                    'method': method1,
                    'des': des,
                    'domain':current_site,
                    'amount' :amount,
                    
                })
            to_email1 = emailto.email
            email1 = EmailMessage(email_subject1, message1, to=[to_email1])
            email1.content_subtype = 'html'
            email1.send()

            # messages.add_message(request, messages.SUCCESS, 'Thank you for contacting us, we would get back to you soon')
            WithdrawModel.objects.create(
            user = request.user,
            pay=method1,
            description = des,
            amount =amount,
            trxid= trx,
        )
            
        except:
            return JsonResponse({'message':'Something happened try again', 'redirect': reverse('main:login'), 'message_type':'danger'})
        
        return JsonResponse({'message':'Withdraw request has been received, Recieve response within 72 hours', 'redirect': reverse('main:login'), 'message_type':'success'})

     
    return render(request, 'funds.html', {'media_url': settings.MEDIA_URL,'invest':invest, 'pay':pay, 'random':random})


@login_required(login_url='/Login')
@csrf_exempt
def  loadmessage(request):
    current_site = get_current_site(request)
    emaill = request.POST.get('email', None)
    paymethod = request.POST.get('paymethod', None)
    amount = request.POST.get('amount', None)
    user = User.objects.get(email=emaill)
    plan = request.POST.get('plan', None)
    mes = Payment_Method.objects.get(name=paymethod)
    msg = Message.objects.all()
    
    session = requests.session()
    url_data = f'https://min-api.cryptocompare.com/data/price?fsym={mes.abrr}&tsyms=USD'
    response = session.get(url_data).json()
    print(response)
    
    # response=requests.get(url_data).json()
    val = int(amount) / response['USD']
    value = round(val, 5)
    print(mes.Message)
    
    print(emaill, user.username)
    email_subject = f'{user.username} Just requested an investment'
    message = render_to_string('investmsg.html', {
            'user': user,
            'domain': current_site.domain,
            'amount': amount,
            'paymethod':paymethod,
            'plan':plan,
            'message':mes.Message,
            'val': value,
        })
    to_email = 'capitalcointradefx@gmail.com'
    email = EmailMessage(email_subject, message, to=[to_email])
    email.content_subtype = 'html'
    email.send()

    
    
    

    email_subject1 = f' Hello {user.username} Investment received'
    message1 = render_to_string('investmsg2.html', {
            'user': user,
            'msg': msg,
            'domain': current_site.domain,
            'amount': amount,
            'paymethod':paymethod,
            'plan':plan,
            'message':mes,
            'val': value,
        })
    to_email1 = emaill
    email = EmailMessage(email_subject1, message1, to=[to_email1])
    email.content_subtype = 'html'
    email.send()

    inplan = Invest_plan.objects.get(name = plan)
    payval = (float(amount) * float(inplan.percent)) + float(amount)
    print(payval, 'this')

    InvestmentModel.objects.create(
        user = request.user,
        plan = inplan,
        amount = amount,
        pay_amount = payval,
        payMethod = paymethod,
        crypto_amount = value

    )
    return render(request, 'includes/message.html', {'media_url': settings.MEDIA_URL,'paymethod': paymethod,'message': mes, 'val':val, 'amount':amount, })
    # 

def  Services(request):
    
    return render(request, 'service.html', {'media_url': settings.MEDIA_URL})

def  package(request):
    invest = Invest_plan.objects.all()
    return render(request, 'package.html', {'media_url': settings.MEDIA_URL,  'invest': invest})

def  noti(request):
    
    return render(request, 'notification.html', {'media_url': settings.MEDIA_URL})

def  testimony(request):
    
    return render(request, 'testimony.html', {'media_url': settings.MEDIA_URL})


def  myinvestView(request):
    invest = InvestmentModel.objects.filter(user=request.user)
    return render(request, 'myinvest.html', {'media_url': settings.MEDIA_URL, 'invest':invest,})

def  reqfundsView(request):
    
    return render(request, 'reqfunds.html', {'media_url': settings.MEDIA_URL})


@csrf_exempt
@staff_required
def  adminpage(request):
    user = User.objects.all()
    ref = Referral.objects.all()
    invest = InvestmentModel.objects.all().order_by('-date')
    if request.method == 'POST':
        current_site = get_current_site(request)
        id = request.POST.get('id', None)
        investment = InvestmentModel.objects.get(pk=id)
        if investment.confirm:
            InvestmentModel.objects.filter(pk=id).update(confirm=False)
            messages.add_message(request, messages.SUCCESS, 'Successfully unconfirmed investments')
            user =  request.user.profile
            user.invested_balance = user.invested_balance.amount-int(investment.amount)
            if investment.payMethod == 'Bitcoin':
                user.btc_balance = float(user.btc_balance.amount) - float(investment.crypto_amount)
            elif investment.payMethod == 'Etherium':
                user.eth_balance = float(user.eth_balance.amount) - float(investment.crypto_amount)
            elif investment.payMethod == 'USDT':
                user.usdt_balance = float(user.usdt_balance.amount) - float(investment.crypto_amount)
            elif investment.payMethod == 'Tron':
                user.tron_balance = float(user.tron_balance.amount) - float(investment.crypto_amount)
                
            user.save()
            print('yes')
        else:
            inv =InvestmentModel.objects.get(pk=id)
            if inv.payout_date:
                payout_date = datetime.now()+timedelta(days=int(inv.plan.return_date))
                print(payout_date)
            InvestmentModel.objects.filter(pk=id).update(confirm=True, payout_date=payout_date)
            messages.add_message(request, messages.SUCCESS, 'Successfully confirmed investments')
            print('no')
            emailto = User.objects.get(username=investment.user.username)
            email_subject1 = f'Your investment has been confirmed'
            message1 = render_to_string('confirminvest.html', {
                    'user': emailto,
                    'amount': investment.amount,
                    'paymethod':investment.payMethod,
                    'domain':current_site,
                    'val': investment.crypto_amount,
                })
            to_email1 = emailto.email
            email1 = EmailMessage(email_subject1, message1, to=[to_email1])
            email1.content_subtype = 'html'
            email1.send()
            user =  request.user.profile
            user.invested_balance = user.invested_balance.amount+int(investment.amount)
            if investment.payMethod == 'Bitcoin':
                user.btc_balance = float(user.btc_balance.amount) + float(investment.crypto_amount)
            elif investment.payMethod == 'Etherium':
                user.eth_balance = float(user.eth_balance.amount) + float(investment.crypto_amount)
            elif investment.payMethod == 'USDT':
                user.usdt_balance = float(user.usdt_balance.amount) + float(investment.crypto_amount)
            elif investment.payMethod == 'Tron':
                user.tron_balance = float(user.tron_balance.amount) + float(investment.crypto_amount)

            user.save()
        print(id)
        return JsonResponse({'message':'Successful', 'redirect': reverse('main:login'), 'message_type':'success'})

    return render(request, 'admin_min.html', {'media_url': settings.MEDIA_URL, 'user':user, 'ref':ref, 'invest':invest})

@csrf_exempt
@staff_required
def  adminmail(request):
    if request.method == 'POST':
        current_site = get_current_site(request)
        emailto = request.POST.get('email', None)
        subject = request.POST.get('subject', None)
        messaged = request.POST.get('des', None)
        email_subject1 = subject
        message1 = render_to_string('sendadminmail.html', {
                'des': messaged,
                'domain':current_site,
            })
        to_email1 = emailto
        email1 = EmailMessage(email_subject1, message1, to=[to_email1])
        email1.content_subtype = 'html'
        email1.send()

        return JsonResponse({'message':'Successful', 'redirect': reverse('main:login'), 'message_type':'success'})

    return render(request, 'adminmailpage.html', {'media_url': settings.MEDIA_URL})


def handler404(request, exception):
    return render(request, '404.html')


def logout_request(request):

    logout(request)
    

    return redirect('main:login')
  

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_form.html'

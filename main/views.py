from django.http import HttpResponseRedirect
from django.shortcuts import  render, redirect
from .forms import NewUserForm,AuthenticationForm
from django.contrib.auth import login, authenticate,logout
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import DockStation,UserOTP
from django.core.mail import send_mail
from django.contrib import messages
from django.views import generic
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt, Radians
from django.db.models import F
from datetime import datetime
from .models import Booking
import stripe
from dock_station import settings
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register

now = datetime.now()
current_time = now.strftime("%H:%M")
# Create your views here.

@csrf_protect
def homepage(request):

	return render(request, 'main/home.html') 


@csrf_protect
def register_request(request):
	if request.method == 'POST':
		get_otp = request.POST.get('otp') #213243 #None
		if get_otp:
			get_usr = request.POST.get('usr')
			usr = User.objects.get(username=get_usr)
			if int(get_otp) == UserOTP.objects.filter(user = usr).last().otp:
				usr.is_active = True
				usr.save()
				messages.success(request, f'Account is Created For {usr.username}')
				return redirect('main:signin')
			else:
				messages.warning(request, f'You Entered a Wrong OTP')
				return render(request, 'main/register.html', {'otp': True, 'usr': usr})
		form = NewUserForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			usr = User.objects.get(username=username)
			usr.email = email
			usr.username = username
			usr.is_active = False
			usr.save()
			usr_otp = random.randint(100000, 999999)
			UserOTP.objects.create(user = usr, otp = usr_otp)
			message = f"Hello {usr.username}\n\nTo authenticate, please enter the following one time password:\n {usr_otp} \n Thanks!"
			send_mail(
				"Welcome to Bikers Hub - Verify Your Email",
				message,
				settings.EMAIL_HOST_USER,
				[usr.email],
				fail_silently = False
				)
			return render(request, 'main/register.html', {'otp': True, 'usr': usr})		

	else:
		form = NewUserForm()
	return render(request, 'main/register.html', {'register_form':form})



@csrf_protect
def signin_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("main:homepage")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="main/signin.html", context={"login_form":form})


@csrf_protect
@method_decorator(login_required(login_url='/'), name='dispatch')
def logout_request(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("main:homepage")


@method_decorator(login_required(login_url='/'), name='dispatch')
class SearchView(generic.ListView):
	template_name = 'main/postcodesearch.html'
	context_object_name='dock_stations'
	
	def get_queryset(self):
		query= DockStation.objects.all()
		if self.request.GET.get('postalcode') and self.request.GET.get('dis'):
			instance = DockStation.objects.get(postcode=self.request.GET.get('postalcode'))
			dlat = Radians(F('latitude') - instance.latitude)
			dlong = Radians(F('longitude') -instance.longitude)

			a = (Power(Sin(dlat / 2), 2) + Cos(Radians(instance.latitude)) * Cos(Radians(F('latitude'))) * Power(Sin(dlong / 2), 2))

			c = 2 * ATan2(Sqrt(a), Sqrt(1 - a))
			d = 6371 * c
			query=query.annotate(distance = d).order_by('distance').filter(distance__lt =self.request.GET.get('dis'))

		return query

	def get_context_data(self, **kwargs) :
		context=super().get_context_data(**kwargs)
		context['postalcode'] =self.request.GET.get('postalcode')
		context['dis'] = int(self.request.GET.get('dis',1))
		context['distance'] = [1,2,3,4,5,6,7,8,9,10]
		return context
	
@method_decorator(login_required(login_url='/'), name='dispatch')	
class BookingView(generic.TemplateView):
	template_name = 'main/bookings.html'

	def get(self,request,id):
		instance=DockStation.objects.get(id=id)
		address= DockStation.objects.values_list('address',flat=True)
		
		bicycle=instance.bicycle.first()
		return render(request,self.template_name,{'current_time':current_time,
      'instance':instance,'address':address,'bicycle':bicycle})

@method_decorator(login_required(login_url='/'), name='dispatch')
class Payment(generic.View):
      
		def post(self, request, *args, **kwargs): 
			address = request.POST.get('address')
			email = request.POST.get('email')
			booking_to = request.POST.get('booking_to')
			leave_time = request.POST.get('leave_time')
			station_id = request.POST.get('station_id')
			station=DockStation.objects.get(id=station_id)
			booking=Booking(booking_postcode=station.postcode,Charges=120,booking_from=station.address,
                         booking_to=booking_to,booking_time=current_time,leave_time=leave_time,email=email,
                         user_address=address,user=request.user )
		
			stripe.api_key = settings.STRIPE_SECRET_KEY
			checkout_session = stripe.checkout.Session.create(
			           customer_email = email,
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                            'name':'Plan ',
                            },
                            'unit_amount': int((120)*100),
                        },
                        'quantity': 1,
                    }
                ],
                mode='payment',
				success_url=request.build_absolute_uri(reverse('main:search') ) + "?session_id={CHECKOUT_SESSION_ID}",
				cancel_url=request.build_absolute_uri(reverse('main:search')),
				) 
			booking.stripe_payment_intent=checkout_session["payment_intent"]
			booking.status=True
			booking.bicycle=station.bicycle.first()
			station.bicycle.remove(station.bicycle.first())
			booking.save()
			
				
			return redirect(checkout_session["url"])

    #Testing card number
    
#     NUMBER         BRAND                            CVC   
# 4242424242424242	Visa	                    Any 3 digits	
# 4000056655665556	Visa (debit)	            Any 3 digits	
# 5555555555554444	Mastercard	                Any 3 digits	
# 2223003122003222	Mastercard (2-series)	    Any 3 digits	
# 5105105105105100	Mastercard (prepaid)	    Any 3 digits	
# 378282246310005	    American Express	         Any 4 digits
# 371449635398431	    American Express	        Any 4 digits
# 6011111111111117	Discover	                Any 3 digits	
# 6011000990139424	Discover	                Any 3 digits	
# 3056930009020004	Diners Club	                Any 3 digits	
# 36227206271667	     Diners Club(14 digit card) Any 3 digits	
# 3566002020360505	JCB	                       Any 3 digits	
# 6200000000000005	UnionPay	                Any 3 digits	


@register.filter(name='check_booking_status')
def check_booking_status(user):
    status = False
    if Booking.objects.filter(bicycle_drop_status=False).filter(user=user).exists():
        status =True
    return status

@register.filter(name='booking_id')
def booking_id(user):
    if Booking.objects.filter(bicycle_drop_status=False).filter(user=user).exists():
        ins=Booking.objects.get(bicycle_drop_status=False,user=user)
    return ins.id

@method_decorator(login_required(login_url='/'), name='dispatch')	
class DropBicycleView(generic.TemplateView):
	template_name = 'main/drop-bicycle.html'

	def get(self,request):
	
		instance=Booking.objects.get(id=request.GET.get('id'))
		address= DockStation.objects.values_list('address',flat=True)
		return render(request,self.template_name,{'now':now,'current_time':current_time,'instance':instance,'address':address})

	def post(self,request):
		instance=Booking.objects.get(id=request.GET.get('id'))
		booking_to=request.POST.get('booking_to')
		instance.booking_to=booking_to
		instance.bicycle_drop_status = True
		instance.drop_datetime = now
		instance.save()
		station=DockStation.objects.get(address=booking_to)
		bicycle = [data.id for data in station.bicycle.all()]
		bicycle.append(station.id)
		station.bicycle.set(bicycle)
		messages.success(request,f'Bicycle successfully dropped at {booking_to}')
		return HttpResponseRedirect(reverse('main:search'))

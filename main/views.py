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

now = datetime.now()

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
def logout_request(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("main:homepage")



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
		context['dis'] = self.request.GET.get('dis')
		context['distance'] = [1,2,3,4,5,6,7,8,9,10]
		return context
	
	
class BookingView(generic.TemplateView):
	template_name = 'main/bookings.html'

	def get(self,request,id):
		instance=DockStation.objects.get(id=id)
		address= DockStation.objects.values_list('address',flat=True)
		current_time = now.strftime("%H:%M")
		return render(request,self.template_name,{'current_time':current_time,
      'instance':instance,'address':address})




# def bookings(request):
# 	return render(request,'main/bookings.html')

# def bikeavailibility(request):
#     return render(request,'main/bookings.html')

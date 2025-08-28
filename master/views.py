from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Testimonial
from .forms import SignupForm, LoginForm

def home(request):
    testimonials = Testimonial.objects.all()
    context = {'testimonials': testimonials}
    return render(request, 'master/index.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'master/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'master/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'master/dashboard.html')

@login_required
def tracking(request):
    if request.method == 'POST':
        tracking_id = request.POST.get('tracking_id')
        # Simulate tracking logic (replace with real logic in production)
        tracking_result = f"Tracking info for ID: {tracking_id} - Status: In Transit"
        return render(request, 'master/tracking.html', {'tracking_result': tracking_result})
    return render(request, 'master/tracking.html')
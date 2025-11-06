from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Testimonial, Shipment
from .forms import SignupForm, LoginForm
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test



def index(request):
    testimonials = Testimonial.objects.all()
    shipments = Shipment.objects.filter(sender=request.user).order_by('-updated_at') if request.user.is_authenticated else []
    context = {
        'testimonials': testimonials,
        'shipments': shipments,
    }
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
            print(f"Auth attempt for {form.cleaned_data['username']}: {user}")
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'master/login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = LoginForm()
    return render(request, 'master/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    shipments = Shipment.objects.filter(sender=request.user).order_by('-updated_at')
    print(f"Debug - User: {request.user.username}, Shipments: {list(shipments)}")
    context = {
        'shipments': shipments,
    }
    return render(request, 'master/dashboard.html', context)

@login_required
def tracking(request):
    if request.method == 'POST':
        tracking_id = request.POST.get('tracking_id')
        shipment = Shipment.objects.filter(tracking_id=tracking_id, sender=request.user).first()
        if shipment:
            tracking_result = f"Tracking info for ID: {shipment.tracking_id} - Status: {shipment.status}, Terminal: {shipment.current_terminal or 'N/A'}, Weight: {shipment.weight} kg, Price: ${shipment.price}"
        else:
            tracking_result = "Shipment not found or not associated with your account."
        return render(request, 'master/tracking.html', {'tracking_result': tracking_result})
    return render(request, 'master/tracking.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('index')
    
    total_users = User.objects.count()
    registered_admins = User.objects.filter(is_staff=True).count()
    total_deliveries = Shipment.objects.count()
    dispatched_packages = Shipment.objects.exclude(status='pending').count()
    pending_deliveries = Shipment.objects.filter(status='pending').count()
    total_weight_on_transit = Shipment.objects.filter(status='on_transit').aggregate(total_weight=Sum('weight'))['total_weight'] or 0
    customer_amounts = User.objects.annotate(total_amount=Sum('sent_shipments__price')).values('username', 'total_amount').order_by('-total_amount')

    context = {
        'total_users': total_users,
        'registered_admins': registered_admins,
        'total_deliveries': total_deliveries,
        'dispatched_packages': dispatched_packages,
        'pending_deliveries': pending_deliveries,
        'total_weight_on_transit': total_weight_on_transit,
        'customer_amounts': customer_amounts,
    }
    return render(request, 'master/admin_dashboard.html', context)

@login_required(login_url='/admin/login/')
@user_passes_test(lambda u: u.is_superuser)

def dashboard_stats(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        total_users = User.objects.count()
        registered_admins = User.objects.filter(is_staff=True).count()
        total_shipments = Shipment.objects.count()
        dispatched_packages = Shipment.objects.filter(status__in=['on_transit', 'arrived', 'completed']).count()
        pending_shipments = Shipment.objects.filter(status='pending').count()

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        daily_dispatch = Shipment.objects.filter(created_at__date=today).count()
        weekly_dispatch = Shipment.objects.filter(created_at__date__gte=week_start).count()
        monthly_dispatch = Shipment.objects.filter(created_at__date__gte=month_start).count()

        data = {
            'total_users': total_users,
            'registered_admins': registered_admins,
            'total_shipments': total_shipments,
            'dispatched_packages': dispatched_packages,
            'pending_shipments': pending_shipments,
            'daily_dispatch': daily_dispatch,
            'weekly_dispatch': weekly_dispatch,
            'monthly_dispatch': monthly_dispatch,
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})

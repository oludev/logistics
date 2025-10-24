from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from django.urls import path
from django.shortcuts import render
import datetime

from .models import Testimonial, Shipment

class CustomAdminSite(admin.AdminSite):
    site_header = "Logistics Admin"
    site_title = "Logistics Admin Portal"
    index_title = "Welcome to the Logistics Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard), name='index'),
        ]
        return custom_urls + urls

    def dashboard(self, request):
        total_users = User.objects.count()
        registered_admins = User.objects.filter(is_staff=True).count()
        total_deliveries = Shipment.objects.count()
        dispatched_packages = Shipment.objects.exclude(status='pending').count()
        pending_deliveries = Shipment.objects.filter(status='pending').count()
        daily_dispatch = Shipment.objects.filter(created_at__gte=timezone.now() - datetime.timedelta(days=1)).count()
        weekly_dispatch = Shipment.objects.filter(created_at__gte=timezone.now() - datetime.timedelta(days=7)).count()
        monthly_dispatch = Shipment.objects.filter(created_at__gte=timezone.now() - datetime.timedelta(days=30)).count()
        total_weight_on_transit = Shipment.objects.filter(status='on_transit').aggregate(total_weight=Sum('weight'))['total_weight'] or 0

        customer_amounts = (
            User.objects.annotate(total_amount=Sum('sent_shipments__price'))
            .values('username', 'total_amount')
            .order_by('-total_amount')
        )

        context = {
            **self.each_context(request),
            'total_users': total_users,
            'registered_admins': registered_admins,
            'total_deliveries': total_deliveries,
            'dispatched_packages': dispatched_packages,
            'pending_deliveries': pending_deliveries,
            'daily_dispatch': daily_dispatch,
            'weekly_dispatch': weekly_dispatch,
            'monthly_dispatch': monthly_dispatch,
            'total_weight_on_transit': total_weight_on_transit,
            'customer_amounts': customer_amounts,
        }
        return render(request, "admin/dashboard.html", context)

# Register models with the custom admin
custom_admin_site = CustomAdminSite(name="custom_admin")
custom_admin_site.register(User, admin.ModelAdmin)
custom_admin_site.register(Testimonial)
custom_admin_site.register(Shipment)

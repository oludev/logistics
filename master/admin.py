from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
import datetime
from .models import Testimonial, Shipment
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'content', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('name', 'content')

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'sender', 'recipient_name', 'status', 'current_terminal', 'arrival_date', 'weight', 'price', 'updated_at')
    list_filter = ('status', 'sender', 'updated_at')
    search_fields = ('tracking_id', 'recipient_name', 'current_terminal')
    list_editable = ('status', 'current_terminal', 'weight', 'price')
    ordering = ('-updated_at',)

    actions = ['mark_as_completed', 'mark_as_arrived', 'mark_as_on_transit', 'generate_invoice']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('sender')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total_users = User.objects.count()
        registered_admins = User.objects.filter(is_staff=True).count()
        total_deliveries = Shipment.objects.count()
        dispatched_packages = Shipment.objects.exclude(status='pending').count()
        pending_deliveries = Shipment.objects.filter(status='pending').count()
        daily_dispatch = Shipment.objects.filter(created_at__gte=timezone.now() - datetime.timedelta(days=1)).count()
        weekly_dispatch = Shipment.objects.filter(created_at__gte=timezone.now() - datetime.timedelta(days=7)).count()
        monthly_dispatch = Shipment.objects.filter(created_at__gte=timezone.now() - datetime.timedelta(days=30)).count()
        total_weight_on_transit = Shipment.objects.filter(status='on_transit').aggregate(total_weight=Sum('weight'))['total_weight'] or 0
        customer_amounts = User.objects.annotate(total_amount=Sum('sent_shipments__price')).values('username', 'total_amount').order_by('-total_amount')

        print(f"Debug - Total Users: {total_users}")
        print(f"Debug - Registered Admins: {registered_admins}")
        print(f"Debug - Total Deliveries: {total_deliveries}")
        print(f"Debug - Dispatched Packages: {dispatched_packages}")
        print(f"Debug - Pending Deliveries: {pending_deliveries}")
        print(f"Debug - Daily Dispatch: {daily_dispatch}")
        print(f"Debug - Weekly Dispatch: {weekly_dispatch}")
        print(f"Debug - Monthly Dispatch: {monthly_dispatch}")
        print(f"Debug - Total Weight on Transit: {total_weight_on_transit}")
        print(f"Debug - Customer Amounts: {list(customer_amounts)}")

        extra_context.update({
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
        })
        return super().changelist_view(request, extra_context)

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected shipments as completed"

    def mark_as_arrived(self, request, queryset):
        queryset.update(status='arrived')
    mark_as_arrived.short_description = "Mark selected shipments as arrived"

    def mark_as_on_transit(self, request, queryset):
        queryset.update(status='on_transit')
    mark_as_on_transit.short_description = "Mark selected shipments as on transit"

    def generate_invoice(self, request, queryset):
        for shipment in queryset:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{shipment.tracking_id}.pdf"'

            doc = SimpleDocTemplate(response, pagesize=letter)
            elements = []

            styles = getSampleStyleSheet()
            elements.append(Paragraph("Invoice", styles['Title']))

            data = [
                ['Tracking ID', shipment.tracking_id],
                ['Sender', shipment.sender.username],
                ['Recipient Name', shipment.recipient_name],
                ['Recipient Address', shipment.recipient_address],
                ['Status', shipment.status],
                ['Weight', f"{shipment.weight} kg"],
                ['Price', f"₦{shipment.price}"],
                ['Created At', shipment.created_at.strftime('%Y-%m-%d %H:%M')],
            ]

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(table)
            doc.build(elements)

            return response

    generate_invoice.short_description = "Generate Invoice for selected shipments"
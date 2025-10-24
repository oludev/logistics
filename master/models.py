from django.db import models
from django.contrib.auth.models import User
import uuid

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, '★' * i) for i in range(1, 6)])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('on_transit', 'On Transit'),
        ('arrived', 'Arrived'),
        ('completed', 'Completed'),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_shipments')
    recipient_name = models.CharField(max_length=100)
    recipient_address = models.TextField()
    tracking_id = models.CharField(max_length=50, unique=True, blank=True)  # Must be blank=True
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_terminal = models.CharField(max_length=100, blank=True, null=True)
    arrival_date = models.DateTimeField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:  # Check if tracking_id is empty
            print("Generating new tracking ID...")  # Debug print
            self.tracking_id = str(uuid.uuid4()).upper()[:8]  # Generate 8-char uppercase UUID
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_id
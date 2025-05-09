from django.db import models
from django.contrib.auth.models import User

class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    id_proof = models.FileField(upload_to='guest_ids/', blank=True)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    ROOM_TYPES = (
        ('S', 'Standard'),
        ('D', 'Deluxe'),
        ('P', 'Premium Suite'),
    )
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=1, choices=ROOM_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField()
    
    def get_type_display(self):
        return dict(self.ROOM_TYPES).get(self.room_type)

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('active', 'Checked In'),
        ('completed', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    )
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField(default=0)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    @property
    def status_color(self):
        return {
            'confirmed': 'primary',
            'active': 'success',
            'completed': 'secondary',
            'cancelled': 'danger',
        }.get(self.status, 'info')
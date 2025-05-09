from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Room, RoomType, Reservation, Service, ReservationService, Payment, Feedback
from django.http import JsonResponse
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import random
import string

def index(request):
    return render(request, 'index.html')

@login_required
def home(request):
    room_types = RoomType.objects.all()
    return render(request, 'home.html', {'room_types': room_types})

@login_required
def search_rooms(request):
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        room_type_id = request.POST.get('room_type')
        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))
        
        # Find conflicting reservations
        conflicting_reservations = Reservation.objects.filter(
            Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
        ).exclude(status__in=['cancelled', 'checked_out'])
        
        # Get available rooms
        available_rooms = Room.objects.filter(
            room_type_id=room_type_id,
            room_type__capacity__gte=(adults + children)
        ).exclude(
            id__in=conflicting_reservations.values('room_id')
        )
        
        room_type = RoomType.objects.get(id=room_type_id)
        
        return render(request, 'home.html', {
            'available_rooms': available_rooms,
            'room_type': room_type,
            'check_in': check_in,
            'check_out': check_out,
            'adults': adults,
            'children': children,
            'search_performed': True
        })
    
    return redirect('home')

@login_required
def book_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))
        special_requests = request.POST.get('special_requests', '')
        
        room = Room.objects.get(id=room_id)
        
        # Create reservation
        reservation = Reservation.objects.create(
            user=request.user,
            room=room,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            children=children,
            special_requests=special_requests,
            status='confirmed'
        )
        
        # Mark room as unavailable
        room.is_available = False
        room.save()
        
        messages.success(request, 'Room booked successfully!')
        return redirect('view_reservation', reservation_id=reservation.id)
    
    return redirect('home')

@login_required
def view_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id, user=request.user)
    services = Service.objects.filter(is_active=True)
    reservation_services = ReservationService.objects.filter(reservation=reservation)
    
    # Calculate total
    nights = (reservation.check_out - reservation.check_in).days
    room_total = reservation.room.room_type.price * nights
    services_total = sum(service.total_price for service in reservation_services)
    total_amount = room_total + services_total
    
    return render(request, 'home.html', {
        'reservation': reservation,
        'services': services,
        'reservation_services': reservation_services,
        'room_total': room_total,
        'services_total': services_total,
        'total_amount': total_amount,
        'nights': nights,
        'viewing_reservation': True
    })

@login_required
def add_service(request, reservation_id):
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        quantity = int(request.POST.get('quantity', 1))
        
        reservation = Reservation.objects.get(id=reservation_id, user=request.user)
        service = Service.objects.get(id=service_id)
        
        ReservationService.objects.create(
            reservation=reservation,
            service=service,
            quantity=quantity
        )
        
        messages.success(request, 'Service added successfully!')
        return redirect('view_reservation', reservation_id=reservation.id)
    
    return redirect('home')

@login_required
def initiate_payment(request, reservation_id):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        reservation = Reservation.objects.get(id=reservation_id, user=request.user)
        
        # Calculate total
        nights = (reservation.check_out - reservation.check_in).days
        room_total = reservation.room.room_type.price * nights
        services_total = sum(
            service.total_price 
            for service in ReservationService.objects.filter(reservation=reservation)
        )
        total_amount = room_total + services_total
        
        # For QR code payment
        if payment_method == 'qr':
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Generate a random transaction ID
            transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            
            qr.add_data(f"hotelpayment:{transaction_id}:{total_amount}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code to payment
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_code_file = ContentFile(buffer.getvalue())
            
            payment = Payment.objects.create(
                reservation=reservation,
                amount=total_amount,
                transaction_id=transaction_id,
                is_successful=False
            )
            payment.qr_code.save(f'qr_{transaction_id}.png', qr_code_file)
            
            reservation.payment_method = payment_method
            reservation.save()
            
            return render(request, 'home.html', {
                'reservation': reservation,
                'payment': payment,
                'total_amount': total_amount,
                'show_qr': True
            })
        
        # For other payment methods
        else:
            payment = Payment.objects.create(
                reservation=reservation,
                amount=total_amount,
                is_successful=True
            )
            
            reservation.payment_method = payment_method
            reservation.payment_status = True
            reservation.save()
            
            messages.success(request, 'Payment completed successfully!')
            return redirect('view_reservation', reservation_id=reservation.id)
    
    return redirect('home')

@login_required
def submit_feedback(request, reservation_id):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')
        
        reservation = Reservation.objects.get(id=reservation_id, user=request.user)
        
        Feedback.objects.create(
            user=request.user,
            reservation=reservation,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('view_reservation', reservation_id=reservation.id)
    
    return redirect('home')

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home.html', {
        'reservations': reservations,
        'showing_reservations': True
    })
    



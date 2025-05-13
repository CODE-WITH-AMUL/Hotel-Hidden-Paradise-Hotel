from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
#code by amul sharma
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')  # Change this to your desired home page
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully.")
            return redirect('login')
    return render(request, 'register.html')

def logout(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard(request):
    # Get the guest associated with the logged-in user
    guest = get_object_or_404(Customer, user=request.user)
    
    # Get current and past reservations
    current_reservations = Reservation.objects.filter(
        guest=guest,
        status__in=['confirmed', 'active']
    ).order_by('check_in_date')
    
    past_reservations = Reservation.objects.filter(
        guest=guest,
        status__in=['completed', 'cancelled']
    ).order_by('-check_out_date')[:5]
    
    # Calculate loyalty points (example)
    loyalty_points = past_reservations.count() * 100
    
    context = {
        'guest': guest,
        'current_reservations': current_reservations,
        'past_reservations': past_reservations,
        'loyalty_points': loyalty_points,
    }
    return render(request, 'guest_dashboard.html', context)
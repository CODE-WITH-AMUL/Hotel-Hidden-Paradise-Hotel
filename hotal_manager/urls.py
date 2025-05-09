from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('search-rooms/', views.search_rooms, name='search_rooms'),
    path('book-room/', views.book_room, name='book_room'),
    path('reservation/<int:reservation_id>/', views.view_reservation, name='view_reservation'),
    path('add-service/<int:reservation_id>/', views.add_service, name='add_service'),
    path('initiate-payment/<int:reservation_id>/', views.initiate_payment, name='initiate_payment'),
    path('submit-feedback/<int:reservation_id>/', views.submit_feedback, name='submit_feedback'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
]
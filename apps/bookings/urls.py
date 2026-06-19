from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.book_appointment, name='book'),
    path('confirmation/<str:reference>/', views.appointment_confirmation, name='confirmation'),
    path('detail/<str:reference>/', views.appointment_detail, name='detail'),
    path('cancel/<str:reference>/', views.cancel_appointment, name='cancel'),
    path('api/slots/', views.available_slots, name='api_slots'),
    path('api/stylist-availability/', views.stylist_availability, name='api_stylist_availability'),
]

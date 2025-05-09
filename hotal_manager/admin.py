from django.contrib import admin
from django.utils.html import format_html
from .models import RoomType, Room, Reservation, Service, ReservationService, Payment, Feedback

class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'floor', 'is_available')
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number',)
    list_editable = ('is_available',)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'check_in', 'check_out', 'status', 'payment_status', 'payment_method')
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('user__username', 'room__room_number')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

class ReservationServiceInline(admin.TabularInline):
    model = ReservationService
    extra = 0

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'amount', 'payment_date', 'is_successful')
    list_filter = ('is_successful',)
    search_fields = ('reservation__id', 'transaction_id')
    
    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="100" />', obj.qr_code.url)
        return "-"
    qr_code_display.short_description = 'QR Code'

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reservation', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved')
    search_fields = ('user__username', 'reservation__id')
    list_editable = ('is_approved',)

admin.site.register(RoomType)
admin.site.register(Room, RoomAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Service)
admin.site.register(ReservationService)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Feedback, FeedbackAdmin)
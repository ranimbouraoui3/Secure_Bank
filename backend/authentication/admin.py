# ...existing code...
from django.contrib import admin
from .models import Account, Beneficiary
from django.utils.html import format_html

class TransactionInline(admin.TabularInline):
    # transaction model is in transactions app; show basic info if installed
    model = None
    extra = 0
    readonly_fields = ('ref', 'amount', 'status', 'created_at', 'transaction_type')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'owner_email', 'currency', 'balance', 'status', 'created_at')
    search_fields = ('account_number', 'owner__email')
    list_filter = ('currency', 'status')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('owner', 'account_number', 'currency', 'balance', 'status')}),
        ('Meta', {'fields': ('metadata',)}),
    )

    def owner_email(self, obj):
        return obj.owner.email
    owner_email.short_description = 'Owner Email'

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number', 'owner_email', 'verification_status', 'verified_at', 'created_at')
    list_filter = ('verification_status',)
    search_fields = ('name', 'account_number', 'owner__email')

    def owner_email(self, obj):
        return obj.owner.email
    owner_email.short_description = 'Owner Email'
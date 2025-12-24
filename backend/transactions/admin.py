"""
Configuration de l'interface d'administration Django pour l'application transactions
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from transactions.models import Transaction, PendingTransaction, TransactionLimit


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Administration pour les transactions
    """
    
    list_display = [
        'reference_number',
        'from_account_link',
        'to_account_or_beneficiary',
        'amount_display',
        'transaction_type',
        'status_badge',
        'otp_verified_icon',
        'initiated_at'
    ]
    
    list_filter = [
        'status',
        'transaction_type',
        'otp_verified',
        'confirmation_email_sent',
        'initiated_at',
        'completed_at'
    ]
    
    search_fields = [
        'reference_number',
        'from_account__iban',
        'to_account__iban',
        'beneficiary__name',
        'beneficiary__iban',
        'description'
    ]
    
    ordering = ['-initiated_at']
    
    readonly_fields = [
        'id',
        'reference_number',
        'initiated_at',
        'completed_at',
        'ip_address',
        'user_agent',
        'otp_verified',
        'confirmation_email_sent',
        'transaction_duration'
    ]
    
    fieldsets = (
        ('Référence', {
            'fields': ('reference_number', 'transaction_type', 'status')
        }),
        ('Comptes et Montant', {
            'fields': (
                'from_account',
                'to_account',
                'beneficiary',
                'amount',
                'currency',
                'description'
            )
        }),
        ('Sécurité', {
            'fields': (
                'otp_verified',
                'ip_address',
                'user_agent'
            )
        }),
        ('Dates', {
            'fields': (
                'initiated_at',
                'completed_at',
                'transaction_duration'
            ),
            'classes': ('collapse',)
        }),
        ('Notifications', {
            'fields': ('confirmation_email_sent',),
            'classes': ('collapse',)
        }),
        ('Erreurs', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_completed',
        'mark_as_failed',
        'export_transactions'
    ]
    
    # Désactiver l'ajout et la modification manuels
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        # Seuls les superusers peuvent modifier
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        # Aucune suppression autorisée
        return False
    
    def from_account_link(self, obj):
        """Lien vers le compte source"""
        url = reverse('admin:accounts_bankaccount_change', args=[obj.from_account.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.from_account.iban
        )
    from_account_link.short_description = 'Compte Source'
    
    def to_account_or_beneficiary(self, obj):
        """Afficher le compte destination ou bénéficiaire"""
        if obj.to_account:
            url = reverse('admin:accounts_bankaccount_change', args=[obj.to_account.id])
            return format_html(
                '<a href="{}">Compte: {}</a>',
                url,
                obj.to_account.iban
            )
        elif obj.beneficiary:
            url = reverse('admin:accounts_beneficiary_change', args=[obj.beneficiary.id])
            return format_html(
                '<a href="{}">Bénéficiaire: {}</a>',
                url,
                obj.beneficiary.name
            )
        return '-'
    to_account_or_beneficiary.short_description = 'Destination'
    
    def amount_display(self, obj):
        """Afficher le montant avec formatage"""
        return format_html(
            '<span style="font-weight: bold; color: #0066cc;">{:.3f} {}</span>',
            obj.amount,
            obj.currency
        )
    amount_display.short_description = 'Montant'
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'pending': 'orange',
            'initiated': 'blue',
            'otp_sent': 'purple',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def otp_verified_icon(self, obj):
        """Icône pour OTP vérifié"""
        if obj.otp_verified:
            return format_html('<span style="color: green; font-size: 18px;">✓</span>')
        return format_html('<span style="color: red; font-size: 18px;">✗</span>')
    otp_verified_icon.short_description = 'OTP'
    
    def transaction_duration(self, obj):
        """Afficher la durée de la transaction"""
        if obj.completed_at:
            duration = obj.completed_at - obj.initiated_at
            seconds = duration.total_seconds()
            if seconds < 60:
                return f"{seconds:.0f} secondes"
            elif seconds < 3600:
                return f"{seconds/60:.1f} minutes"
            else:
                return f"{seconds/3600:.1f} heures"
        return "En cours..."
    transaction_duration.short_description = 'Durée'
    
    def mark_as_completed(self, request, queryset):
        """Marquer les transactions comme complétées"""
        count = queryset.update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f"{count} transaction(s) marquée(s) comme complétée(s).")
    mark_as_completed.short_description = "Marquer comme complétée"

    def mark_as_failed(self, request, queryset):
        """Marquer les transactions comme échouées"""
        count = queryset.update(
            status='failed',
            completed_at=timezone.now()
        )
        self.message_user(request, f"{count} transaction(s) marquée(s) comme échouée(s).")
    mark_as_failed.short_description = "Marquer comme échouée"


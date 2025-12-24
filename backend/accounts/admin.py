"""
Configuration de l'interface d'administration Django pour l'application accounts
Permet une gestion complète via le panel admin Django
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from accounts.models import User, BankAccount, Beneficiary, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administration personnalisée pour le modèle User
    """
    
    # Affichage de la liste
    list_display = [
        'email', 
        'name', 
        'phone', 
        'account_status_badge',
        'is_2fa_enabled',
        'failed_login_attempts',
        'account_count',
        'created_at'
    ]
    
    list_filter = [
        'account_status',
        'is_2fa_enabled',
        'is_staff',
        'is_superuser',
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'email',
        'name',
        'phone',
        'username'
    ]
    
    ordering = ['-created_at']
    
    # Organisation des champs dans le formulaire de détail
    fieldsets = (
        ('Informations de Base', {
            'fields': ('email', 'username', 'name', 'phone', 'password')
        }),
        ('Statut du Compte', {
            'fields': ('account_status', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Sécurité', {
            'fields': (
                'is_2fa_enabled',
                'otp_secret',
                'failed_login_attempts',
                'account_locked_until',
                'last_password_change'
            )
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Dates Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_login',
        'date_joined',
        'last_password_change',
        'otp_secret'
    ]
    
    # Champs pour la création d'un nouvel utilisateur
    add_fieldsets = (
        ('Informations Essentielles', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'name', 'phone', 'password1', 'password2'),
        }),
        ('Statut', {
            'fields': ('account_status', 'is_2fa_enabled')
        })
    )
    
    # Actions personnalisées
    actions = [
        'activate_accounts',
        'suspend_accounts',
        'reset_failed_logins',
        'enable_2fa',
        'disable_2fa'
    ]
    
    def account_status_badge(self, obj):
        """Afficher le statut du compte avec des couleurs"""
        colors = {
            'active': 'green',
            'suspended': 'orange',
            'locked': 'red',
            'closed': 'gray'
        }
        color = colors.get(obj.account_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_account_status_display()
        )
    account_status_badge.short_description = 'Statut'
    
    def account_count(self, obj):
        """Afficher le nombre de comptes bancaires"""
        count = obj.accounts.count()
        if count > 0:
            url = reverse('admin:accounts_bankaccount_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} compte(s)</a>', url, count)
        return '0'
    account_count.short_description = 'Comptes'
    
    # Actions en masse
    def activate_accounts(self, request, queryset):
        """Activer les comptes sélectionnés"""
        updated = queryset.update(account_status='active', account_locked_until=None)
        self.message_user(request, f'{updated} compte(s) activé(s).')
    activate_accounts.short_description = 'Activer les comptes sélectionnés'
    
    def suspend_accounts(self, request, queryset):
        """Suspendre les comptes sélectionnés"""
        updated = queryset.update(account_status='suspended')
        self.message_user(request, f'{updated} compte(s) suspendu(s).')
    suspend_accounts.short_description = 'Suspendre les comptes sélectionnés'
    
    def reset_failed_logins(self, request, queryset):
        """Réinitialiser les tentatives de connexion échouées"""
        updated = queryset.update(failed_login_attempts=0, account_locked_until=None)
        self.message_user(request, f'{updated} compteur(s) réinitialisé(s).')
    reset_failed_logins.short_description = 'Réinitialiser les tentatives échouées'
    
    def enable_2fa(self, request, queryset):
        """Activer l'authentification 2FA"""
        updated = queryset.update(is_2fa_enabled=True)
        self.message_user(request, f'2FA activé pour {updated} utilisateur(s).')
    enable_2fa.short_description = 'Activer 2FA'
    
    def disable_2fa(self, request, queryset):
        """Désactiver l'authentification 2FA"""
        updated = queryset.update(is_2fa_enabled=False)
        self.message_user(request, f'2FA désactivé pour {updated} utilisateur(s).')
    disable_2fa.short_description = 'Désactiver 2FA'


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    """
    Administration pour les comptes bancaires
    """
    
    list_display = [
        'iban',
        'user_link',
        'name',
        'balance_display',
        'account_type',
        'status_badge',
        'created_at'
    ]
    
    list_filter = [
        'account_type',
        'status',
        'currency',
        'created_at'
    ]
    
    search_fields = [
        'iban',
        'user__email',
        'user__name',
        'name'
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'last_transaction_date'
    ]
    
    fieldsets = (
        ('Informations du Compte', {
            'fields': ('user', 'name', 'iban', 'account_type')
        }),
        ('Finances', {
            'fields': ('balance', 'currency')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'last_transaction_date'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'activate_accounts',
        'suspend_accounts',
        'export_to_csv'
    ]
    
    def user_link(self, obj):
        """Lien vers l'utilisateur propriétaire"""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'Utilisateur'
    
    def balance_display(self, obj):
        """Afficher le solde avec formatage"""
        color = 'green' if obj.balance > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.3f} {}</span>',
            color,
            obj.balance,
            obj.currency
        )
    balance_display.short_description = 'Solde'
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'active': 'green',
            'suspended': 'orange',
            'closed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def activate_accounts(self, request, queryset):
        """Activer les comptes sélectionnés"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} compte(s) activé(s).')
    activate_accounts.short_description = 'Activer les comptes'
    
    def suspend_accounts(self, request, queryset):
        """Suspendre les comptes"""
        updated = queryset.update(status='suspended')
        self.message_user(request, f'{updated} compte(s) suspendu(s).')
    suspend_accounts.short_description = 'Suspendre les comptes'


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    """
    Administration pour les bénéficiaires
    """
    
    list_display = [
        'name',
        'iban',
        'owner_link',
        'bank_name',
        'bank_type',
        'status_badge',
        'created_at'
    ]
    
    list_filter = [
        'bank_type',
        'status',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'iban',
        'bank_name',
        'owner__email',
        'owner__name'
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Informations du Bénéficiaire', {
            'fields': ('owner', 'name', 'iban', 'bank_name')
        }),
        ('Type de Banque', {
            'fields': ('bank_type', 'swift_code')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'verify_beneficiaries',
        'reject_beneficiaries'
    ]
    
    def owner_link(self, obj):
        """Lien vers le propriétaire"""
        url = reverse('admin:accounts_user_change', args=[obj.owner.id])
        return format_html('<a href="{}">{}</a>', url, obj.owner.email)
    owner_link.short_description = 'Propriétaire'
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'pending_verification': 'orange',
            'verified': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def verify_beneficiaries(self, request, queryset):
        """Vérifier les bénéficiaires"""
        updated = queryset.update(status='verified')
        self.message_user(request, f'{updated} bénéficiaire(s) vérifié(s).')
    verify_beneficiaries.short_description = 'Vérifier les bénéficiaires'
    
    def reject_beneficiaries(self, request, queryset):
        """Rejeter les bénéficiaires"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} bénéficiaire(s) rejeté(s).')
    reject_beneficiaries.short_description = 'Rejeter les bénéficiaires'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Administration pour les logs d'audit (lecture seule)
    """
    
    list_display = [
        'timestamp',
        'user_link',
        'action_badge',
        'status_badge',
        'amount_display',
        'ip_address'
    ]
    
    list_filter = [
        'action',
        'status',
        'timestamp'
    ]
    
    search_fields = [
        'user__email',
        'user__name',
        'action',
        'description',
        'ip_address'
    ]
    
    ordering = ['-timestamp']
    
    # Lecture seule - aucune modification autorisée
    readonly_fields = [
        'id',
        'user',
        'action',
        'status',
        'description',
        'amount',
        'ip_address',
        'user_agent',
        'timestamp'
    ]
    
    fieldsets = (
        ('Action', {
            'fields': ('timestamp', 'user', 'action', 'status')
        }),
        ('Détails', {
            'fields': ('description', 'amount')
        }),
        ('Sécurité', {
            'fields': ('ip_address', 'user_agent')
        }),
    )
    
    # Désactiver les actions de modification
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Seuls les superusers peuvent supprimer les logs
        return request.user.is_superuser
    
    def user_link(self, obj):
        """Lien vers l'utilisateur"""
        if obj.user:
            url = reverse('admin:accounts_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_link.short_description = 'Utilisateur'
    
    def action_badge(self, obj):
        """Badge pour l'action"""
        colors = {
            'login': 'blue',
            'logout': 'gray',
            'failed_login': 'red',
            'transfer_completed': 'green',
            'transfer_failed': 'red',
            'suspicious_activity': 'red'
        }
        color = colors.get(obj.action, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Action'
    
    def status_badge(self, obj):
        """Badge pour le statut"""
        colors = {
            'success': 'green',
            'failed': 'red',
            'warning': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def amount_display(self, obj):
        """Afficher le montant s'il existe"""
        if obj.amount:
            return format_html(
                '<span style="font-weight: bold;">{:.3f} TND</span>',
                obj.amount
            )
        return '-'
    amount_display.short_description = 'Montant'


# Personnalisation du site d'administration
admin.site.site_header = "Administration Application Bancaire"
admin.site.site_title = "Banking Admin"
admin.site.index_title = "Tableau de Bord d'Administration"
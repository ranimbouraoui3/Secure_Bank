"""
URL Configuration pour l'application bancaire
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

# Import des vues
from authentication import views as auth_views
from accounts import views as accounts_views
from transactions import views as transactions_views


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # ==================== AUTHENTICATION ENDPOINTS ====================
    path('api/auth/register', auth_views.register_user, name='register'),
    path('api/auth/login', auth_views.login_user, name='login'),
    path('api/auth/logout', auth_views.logout_user, name='logout'),
    path('api/auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    # ==================== PROFILE ENDPOINTS ====================
    path('api/profile', auth_views.get_profile, name='profile'),
    path('api/profile/update', auth_views.update_profile, name='profile_update'),
    path('api/profile/change-password', auth_views.change_password, name='change_password'),
    
    # ==================== OTP ENDPOINTS ====================
    path('api/otp/send', auth_views.send_otp, name='send_otp'),
    path('api/otp/verify', auth_views.verify_otp, name='verify_otp'),
    
    # ==================== ACCOUNT ENDPOINTS ====================
    path('api/accounts', accounts_views.get_accounts, name='accounts_list'),
    path('api/accounts/<uuid:account_id>', accounts_views.get_account_detail, name='account_detail'),
    
    # ==================== BENEFICIARY ENDPOINTS ====================
    path('api/beneficiaries', accounts_views.get_beneficiaries, name='beneficiaries_list'),
    path('api/beneficiaries/add', accounts_views.add_beneficiary, name='add_beneficiary'),
    path('api/beneficiaries/<uuid:beneficiary_id>', accounts_views.delete_beneficiary, name='delete_beneficiary'),
    path('api/beneficiaries/<uuid:beneficiary_id>/update', accounts_views.update_beneficiary, name='update_beneficiary'),
    
    # ==================== TRANSACTION ENDPOINTS ====================
    path('api/transactions', transactions_views.get_transactions, name='transactions_list'),
    path('api/transactions/<uuid:transaction_id>', transactions_views.get_transaction_detail, name='transaction_detail'),
    path('api/transactions/initiate', transactions_views.initiate_transaction, name='initiate_transaction'),
    path('api/transactions/verify-and-execute', transactions_views.verify_and_execute_transaction, name='execute_transaction'),
    
    # ==================== AUDIT ENDPOINTS ====================
    path('api/audit/logs', accounts_views.get_audit_logs, name='audit_logs'),
]

# Ajouter les fichiers statiques en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Personnalisation de l'admin
admin.site.site_header = "Banking Application Administration"
admin.site.site_title = "Banking Admin"
admin.site.index_title = "Welcome to Banking Administration"
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils import timezone
from accounts.utils import create_user_bank_account

from accounts.models import User, AuditLog
from accounts.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer
)
from accounts.utils import (
    get_client_ip,
    get_user_agent,
    send_email,
    generate_otp,
    verify_otp_code,
    cache_otp
)

import logging

logger = logging.getLogger('security')


def create_audit_log(user, action, status_result, ip_address, user_agent, description="", amount=None):
    """Créer un log d'audit"""
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            status=status_result,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
            amount=amount
        )
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']

        # === Create bank account if not exists ===
        if not user.bank_accounts.exists():
            account = create_user_bank_account(user)
        else:
            account = user.bank_accounts.first()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Update last_login
        user.last_login = timezone.now()
        user.save()

        # Audit log
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        create_audit_log(
            user=user,
            action='login',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"User logged in successfully"
        )

        # Return response with linked bank account
        return Response({
            'success': True,
            'token': access_token,
            'refreshToken': refresh_token,
            'user': UserSerializer(user).data,
            'account': {
                'iban': account.iban,
                'name': account.name,
                'balance': account.balance
            } if account else None
        }, status=status.HTTP_200_OK)

    # Failed login
    email = request.data.get('email', '')
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    try:
        failed_user = User.objects.get(email=email.lower())
        create_audit_log(
            user=failed_user,
            action='failed_login',
            status_result='failed',
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Failed login attempt"
        )
    except User.DoesNotExist:
        pass

    return Response({
        'success': False,
        'error': serializer.errors
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    POST /api/auth/logout
    Déconnexion utilisateur
    """
    try:
        # Blacklister le refresh token
        refresh_token = request.data.get('refreshToken')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Créer un log d'audit
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        create_audit_log(
            user=request.user,
            action='logout',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description="User logged out"
        )
        
        logger.info(f"User logged out: {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Logout error for {request.user.email}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """
    GET /api/profile
    Récupérer le profil utilisateur
    """
    serializer = UserSerializer(request.user)
    
    return Response({
        'success': True,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    PUT /api/profile
    Mettre à jour le profil utilisateur
    """
    serializer = UserProfileUpdateSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Créer un log d'audit
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        create_audit_log(
            user=user,
            action='profile_update',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Profile updated"
        )
        
        logger.info(f"Profile updated for user: {user.email}")
        
        # Envoyer un email de confirmation
        send_email(
            to_email=user.email,
            subject='Confirmation de mise à jour de profil',
            template='profile_updated',
            context={'user': user}
        )
        
        user_serializer = UserSerializer(user)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'error': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    POST /api/profile/change-password
    Changer le mot de passe utilisateur
    """
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.last_password_change = timezone.now()
        user.save()
        
        # Créer un log d'audit
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        create_audit_log(
            user=user,
            action='password_change',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description="Password changed successfully"
        )
        
        logger.info(f"Password changed for user: {user.email}")
        
        # Envoyer un email de confirmation
        send_email(
            to_email=user.email,
            subject='Confirmation de changement de mot de passe',
            template='password_changed',
            context={'user': user}
        )
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'error': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """
    POST /api/otp/send
    Envoyer un code OTP par email
    """
    email = request.data.get('email', '').lower()
    otp_type = request.data.get('type', 'transfer')
    
    try:
        user = User.objects.get(email=email)
        
        # Générer et cacher l'OTP
        otp_code = generate_otp()
        cache_otp(email, otp_code, otp_type)
        
        # Envoyer l'OTP par email
        send_email(
            to_email=user.email,
            subject=f'Code OTP - {otp_type}',
            template='otp_email',
            context={
                'user': user,
                'otp_code': otp_code,
                'otp_type': otp_type,
                'expires_in': 5  # minutes
            }
        )
        
        logger.info(f"OTP sent to {email} for {otp_type}")
        
        return Response({
            'success': True,
            'message': 'OTP sent successfully',
            'expiresIn': 300  # 5 minutes en secondes
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        logger.warning(f"OTP request for non-existent user: {email}")
        return Response({
            'success': False,
            'error': 'User not found'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    POST /api/otp/verify
    Vérifier un code OTP
    """
    email = request.data.get('email', '').lower()
    otp_code = request.data.get('otp', '')
    otp_type = request.data.get('type', 'transfer')
    
    if verify_otp_code(email, otp_code, otp_type):
        logger.info(f"OTP verified successfully for {email}")
        
        return Response({
            'success': True,
            'message': 'OTP verified successfully',
            'token': 'verification-token'  # Token pour actions suivantes
        }, status=status.HTTP_200_OK)
    
    logger.warning(f"Invalid OTP attempt for {email}")
    
    return Response({
        'success': False,
        'error': 'Invalid OTP or OTP expired'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    POST /api/auth/register
    Enregistrer un nouvel utilisateur et créer automatiquement son compte bancaire unique.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Créer un compte bancaire unique
        account = create_user_bank_account(user)

        # Créer un log d'audit
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        create_audit_log(
            user=user,
            action='user_registered',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"User registered and bank account created: {account.iban if account else 'failed'}"
        )

        # Envoyer email de bienvenue
        send_email(user.email, subject="Bienvenue", message="Votre compte a été créé avec succès !")

        return Response({
            'success': True,
            'message': 'Utilisateur enregistré avec succès',
            'user': UserSerializer(user).data,
            'account': {
                'iban': account.iban,
                'name': account.name,
                'balance': account.balance
            } if account else None
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
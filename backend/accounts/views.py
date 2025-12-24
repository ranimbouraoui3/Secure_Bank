from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from accounts.models import BankAccount, Beneficiary, AuditLog
from accounts.serializers import (
    BankAccountSerializer,
    BeneficiarySerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    AuditLogSerializer
)
from accounts.utils import get_client_ip, get_user_agent, send_email

import logging

logger = logging.getLogger('django')


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


# ==================== USER REGISTRATION ====================

@api_view(['POST'])
def register_user(request):
    """
    POST /api/register
    Enregistrer un nouvel utilisateur et créer automatiquement son compte bancaire
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Créer un compte bancaire principal
        BankAccount.objects.create(
            user=user,
            name=f"Compte principal de {user.name}",
            iban=BankAccount.generate_iban(),
            account_type='checking',
            balance=0,
            status='active'
        )

        # Créer un log d'audit
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        create_audit_log(
            user=user,
            action='user_registered',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"User registered: {user.email}"
        )

        # Optionnel : envoyer un email de bienvenue
        send_email(user.email, subject="Bienvenue", message="Votre compte a été créé avec succès !")

        return Response({
            'success': True,
            'message': 'Utilisateur enregistré avec succès',
            'user': UserRegistrationSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# ==================== LOGIN ====================

@api_view(['POST'])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    user.reset_failed_login()  # réinitialise le compteur après succès

    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'success': True,
        'token': token.key,
        'user': {"email": user.email, "id": user.id}
    }, status=200)


# ==================== BANK ACCOUNTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accounts(request):
    accounts = BankAccount.objects.filter(user=request.user)
    serializer = BankAccountSerializer(accounts, many=True)
    logger.info(f"User {request.user.email} retrieved {accounts.count()} accounts")
    return Response({'success': True, 'accounts': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_detail(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id, user=request.user)
    serializer = BankAccountSerializer(account)
    return Response({'success': True, 'account': serializer.data}, status=status.HTTP_200_OK)


# ==================== BENEFICIARIES ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_beneficiaries(request):
    beneficiaries = Beneficiary.objects.filter(owner=request.user)
    serializer = BeneficiarySerializer(beneficiaries, many=True)
    logger.info(f"User {request.user.email} retrieved {beneficiaries.count()} beneficiaries")
    return Response({'success': True, 'beneficiaries': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_beneficiary(request):
    serializer = BeneficiarySerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        beneficiary = serializer.save()
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        create_audit_log(
            user=request.user,
            action='beneficiary_added',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Beneficiary added: {beneficiary.name} - {beneficiary.iban}"
        )
        logger.info(f"Beneficiary added by {request.user.email}: {beneficiary.name}")
        return Response({
            'success': True,
            'message': 'Beneficiary added successfully',
            'beneficiary': BeneficiarySerializer(beneficiary).data
        }, status=status.HTTP_201_CREATED)

    return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_beneficiary(request, beneficiary_id):
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id, owner=request.user)
    beneficiary_name = beneficiary.name
    beneficiary_iban = beneficiary.iban
    beneficiary.delete()

    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    create_audit_log(
        user=request.user,
        action='beneficiary_deleted',
        status_result='success',
        ip_address=ip_address,
        user_agent=user_agent,
        description=f"Beneficiary deleted: {beneficiary_name} - {beneficiary_iban}"
    )
    logger.info(f"Beneficiary deleted by {request.user.email}: {beneficiary_name}")
    return Response({'success': True, 'message': 'Beneficiary deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_beneficiary(request, beneficiary_id):
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id, owner=request.user)
    data = request.data.copy()
    data.pop('iban', None)  # IBAN non modifiable

    serializer = BeneficiarySerializer(beneficiary, data=data, partial=True, context={'request': request})
    if serializer.is_valid():
        beneficiary = serializer.save()
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        create_audit_log(
            user=request.user,
            action='beneficiary_updated',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Beneficiary updated: {beneficiary.name}"
        )
        logger.info(f"Beneficiary updated by {request.user.email}: {beneficiary.name}")
        return Response({
            'success': True,
            'message': 'Beneficiary updated successfully',
            'beneficiary': BeneficiarySerializer(beneficiary).data
        }, status=status.HTTP_200_OK)

    return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ==================== AUDIT LOGS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audit_logs(request):
    if not request.user.is_staff:
        return Response({'success': False, 'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.query_params.get('userId')
    action = request.query_params.get('action')
    start_date = request.query_params.get('startDate')
    end_date = request.query_params.get('endDate')
    limit = int(request.query_params.get('limit', 50))

    logs = AuditLog.objects.all()
    if user_id:
        logs = logs.filter(user__id=user_id)
    if action:
        logs = logs.filter(action=action)
    if start_date:
        logs = logs.filter(timestamp__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__lte=end_date)

    logs = logs[:limit]
    serializer = AuditLogSerializer(logs, many=True)
    return Response({'success': True, 'logs': serializer.data, 'total': logs.count()}, status=status.HTTP_200_OK)

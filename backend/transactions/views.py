from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

from accounts.models import BankAccount, Beneficiary, AuditLog
from transactions.models import Transaction, PendingTransaction, TransactionLimit
from transactions.serializers import TransactionSerializer
from accounts.utils import (
    get_client_ip,
    get_user_agent,
    send_email,
    generate_otp,
    cache_otp,
    verify_otp_code
)

import logging

logger = logging.getLogger('transactions')


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
@permission_classes([IsAuthenticated])
def initiate_transaction(request):
    """
    POST /api/transactions/initiate
    Initier une nouvelle transaction (avant vérification OTP)
    """
    from_account_id = request.data.get('fromAccountId')
    to_beneficiary_id = request.data.get('toBeneficiaryId')
    amount = Decimal(str(request.data.get('amount', 0)))
    description = request.data.get('description', '')
    
    # Validation de base
    if not all([from_account_id, to_beneficiary_id, amount]):
        return Response({
            'success': False,
            'error': 'Missing required fields'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if amount <= 0:
        return Response({
            'success': False,
            'error': 'Invalid amount'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Récupérer le compte source
        from_account = get_object_or_404(
            BankAccount,
            id=from_account_id,
            user=request.user,
            status='active'
        )
        
        # Récupérer le bénéficiaire
        beneficiary = get_object_or_404(
            Beneficiary,
            id=to_beneficiary_id,
            owner=request.user,
            status='verified'
        )
        
        # Vérifier le solde
        if from_account.balance < amount:
            return Response({
                'success': False,
                'error': 'Insufficient funds'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier les limites de transaction
        transaction_limit, _ = TransactionLimit.objects.get_or_create(user=request.user)
        can_transfer, error_msg = transaction_limit.can_transfer(amount)
        
        if not can_transfer:
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Générer et envoyer l'OTP
        otp_code = generate_otp()
        
        # Créer une transaction en attente
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        pending_txn = PendingTransaction.objects.create(
            user=request.user,
            from_account=from_account,
            beneficiary=beneficiary,
            amount=amount,
            description=description,
            otp_code=otp_code,
            otp_expires_at=timezone.now() + timezone.timedelta(seconds=settings.OTP_EXPIRY_TIME),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Envoyer l'OTP par email
        send_email(
            to_email=request.user.email,
            subject='Code OTP pour votre virement',
            template='otp_transfer',
            context={
                'user': request.user,
                'otp_code': otp_code,
                'amount': amount,
                'beneficiary': beneficiary.name,
                'expires_in': 5
            }
        )
        
        # Créer un log d'audit
        create_audit_log(
            user=request.user,
            action='transfer_initiated',
            status_result='success',
            ip_address=ip_address,
            user_agent=user_agent,
            description=f"Transfer initiated to {beneficiary.name}",
            amount=amount
        )
        
        logger.info(
            f"Transaction initiated by {request.user.email}: "
            f"{amount} TND to {beneficiary.name}"
        )
        
        return Response({
            'success': True,
            'transactionId': str(pending_txn.id),
            'amount': float(amount),
            'otpSent': True,
            'message': 'OTP sent to registered email'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error initiating transaction: {str(e)}")
        return Response({
            'success': False,
            'error': 'Transaction initiation failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_and_execute_transaction(request):
    """
    POST /api/transactions/verify-and-execute
    Vérifier l'OTP et exécuter la transaction avec ACID
    """
    transaction_id = request.data.get('transactionId')
    otp_code = request.data.get('otp')
    
    if not all([transaction_id, otp_code]):
        return Response({
            'success': False,
            'error': 'Missing required fields'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Récupérer la transaction en attente
        pending_txn = get_object_or_404(
            PendingTransaction,
            id=transaction_id,
            user=request.user,
            is_consumed=False
        )
        
        # Vérifier l'OTP
        if not pending_txn.verify_otp(otp_code):
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            
            create_audit_log(
                user=request.user,
                action='transfer_failed',
                status_result='failed',
                ip_address=ip_address,
                user_agent=user_agent,
                description="Invalid or expired OTP",
                amount=pending_txn.amount
            )
            
            logger.warning(f"Invalid OTP for transaction {transaction_id}")
            
            return Response({
                'success': False,
                'error': 'Invalid OTP or OTP expired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marquer la transaction en attente comme consommée
        pending_txn.is_consumed = True
        pending_txn.save()
        
        # TRANSACTION ACID - DÉBUT
        with db_transaction.atomic():
            # 1. Débiter le compte source
            from_account = pending_txn.from_account
            from_account.debit(pending_txn.amount)
            
            # 2. Vérifier si le bénéficiaire a un compte dans notre système
            to_account = None
            try:
                to_account = BankAccount.objects.get(
                    iban=pending_txn.beneficiary.iban,
                    status='active'
                )
                # Créditer le compte destination (transfert interne)
                to_account.credit(pending_txn.amount)
            except BankAccount.DoesNotExist:
                # Transfert externe - pas de crédit automatique
                pass
            
            # 3. Créer la transaction définitive
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            
            final_transaction = Transaction.objects.create(
                from_account=from_account,
                to_account=to_account,
                beneficiary=pending_txn.beneficiary,
                transaction_type='transfer',
                amount=pending_txn.amount,
                currency='TND',
                description=pending_txn.description,
                reference_number=Transaction.generate_reference_number(),
                status='completed',
                ip_address=ip_address,
                user_agent=user_agent,
                otp_verified=True
            )
            
            final_transaction.completed_at = timezone.now()
            final_transaction.save()
            
            # 4. Mettre à jour les limites de transaction
            transaction_limit = TransactionLimit.objects.get(user=request.user)
            transaction_limit.add_to_daily_used(pending_txn.amount)
            
            # 5. Créer un log d'audit
            create_audit_log(
                user=request.user,
                action='transfer_completed',
                status_result='success',
                ip_address=ip_address,
                user_agent=user_agent,
                description=f"Transfer completed to {pending_txn.beneficiary.name}",
                amount=pending_txn.amount
            )
        
        # TRANSACTION ACID - FIN
        
        # Envoyer l'email de confirmation (asynchrone - hors transaction)
        try:
            send_email(
                to_email=request.user.email,
                subject='Confirmation de virement',
                template='transfer_confirmation',
                context={
                    'user': request.user,
                    'transaction': final_transaction,
                    'beneficiary': pending_txn.beneficiary,
                    'amount': pending_txn.amount,
                    'reference_number': final_transaction.reference_number,
                    'date': final_transaction.completed_at
                }
            )
            final_transaction.confirmation_email_sent = True
            final_transaction.save()
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {str(e)}")
        
        logger.info(
            f"Transaction completed: {final_transaction.reference_number} - "
            f"{pending_txn.amount} TND"
        )
        
        return Response({
            'success': True,
            'message': 'Transaction completed successfully',
            'transaction': {
                'id': str(final_transaction.id),
                'amount': float(final_transaction.amount),
                'beneficiary': pending_txn.beneficiary.name,
                'fromAccount': from_account.name,
                'status': final_transaction.status,
                'timestamp': final_transaction.completed_at.isoformat(),
                'referenceNumber': final_transaction.reference_number,
                'confirmationEmailSent': final_transaction.confirmation_email_sent
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error executing transaction: {str(e)}")
        
        # Log de l'échec
        try:
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            create_audit_log(
                user=request.user,
                action='transfer_failed',
                status_result='failed',
                ip_address=ip_address,
                user_agent=user_agent,
                description=f"Transaction execution failed: {str(e)}"
            )
        except:
            pass
        
        return Response({
            'success': False,
            'error': 'Transaction execution failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    """
    GET /api/transactions
    Récupérer l'historique des transactions
    """
    # Filtres optionnels
    account_id = request.query_params.get('accountId')
    txn_type = request.query_params.get('type')  # 'sent' or 'received'
    txn_status = request.query_params.get('status')
    start_date = request.query_params.get('startDate')
    end_date = request.query_params.get('endDate')
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))
    
    # Récupérer les comptes de l'utilisateur
    user_accounts = BankAccount.objects.filter(user=request.user)
    
    # Construire la requête
    if account_id:
        transactions = Transaction.objects.filter(
            from_account__id=account_id,
            from_account__user=request.user
        )
    else:
        transactions = Transaction.objects.filter(
            from_account__in=user_accounts
        ) | Transaction.objects.filter(
            to_account__in=user_accounts
        )
    
    # Appliquer les filtres
    if txn_type == 'sent':
        transactions = transactions.filter(from_account__user=request.user)
    elif txn_type == 'received':
        transactions = transactions.filter(to_account__user=request.user)
    
    if txn_status:
        transactions = transactions.filter(status=txn_status)
    
    if start_date:
        transactions = transactions.filter(initiated_at__gte=start_date)
    
    if end_date:
        transactions = transactions.filter(initiated_at__lte=end_date)
    
    # Pagination
    total = transactions.count()
    transactions = transactions.distinct()[offset:offset + limit]
    
    serializer = TransactionSerializer(
        transactions,
        many=True,
        context={'request': request}
    )
    
    logger.info(f"User {request.user.email} retrieved {len(serializer.data)} transactions")
    
    return Response({
        'success': True,
        'transactions': serializer.data,
        'total': total,
        'limit': limit,
        'offset': offset
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transaction_detail(request, transaction_id):
    """
    GET /api/transactions/{transactionId}
    Récupérer les détails d'une transaction spécifique
    """
    # Récupérer les comptes de l'utilisateur
    user_accounts = BankAccount.objects.filter(user=request.user)
    
    # Vérifier que la transaction appartient à l'utilisateur
    transaction_obj = get_object_or_404(
        Transaction,
        id=transaction_id
    )
    
    if (transaction_obj.from_account not in user_accounts and 
        transaction_obj.to_account not in user_accounts):
        return Response({
            'success': False,
            'error': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TransactionSerializer(
        transaction_obj,
        context={'request': request}
    )
    
    return Response({
        'success': True,
        'transaction': serializer.data
    }, status=status.HTTP_200_OK)
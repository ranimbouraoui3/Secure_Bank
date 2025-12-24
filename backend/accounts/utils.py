import secrets
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache
import logging

from accounts.models import BankAccount

logger = logging.getLogger('django')


def get_client_ip(request):
    """Récupérer l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def get_user_agent(request):
    """Récupérer le user agent du client"""
    return request.META.get('HTTP_USER_AGENT', 'Unknown')


def generate_otp(length=6):
    """Générer un code OTP aléatoire"""
    digits = string.digits
    otp = ''.join(secrets.choice(digits) for _ in range(length))
    return otp


def cache_otp(identifier, otp_code, otp_type='transfer'):
    """Mettre en cache un code OTP"""
    cache_key = f'otp:{otp_type}:{identifier}'
    cache.set(cache_key, otp_code, timeout=settings.OTP_EXPIRY_TIME)
    logger.info(f"OTP cached for {identifier} - Type: {otp_type}")


def verify_otp_code(identifier, otp_code, otp_type='transfer'):
    """Vérifier un code OTP depuis le cache"""
    cache_key = f'otp:{otp_type}:{identifier}'
    cached_otp = cache.get(cache_key)
    
    if cached_otp and cached_otp == otp_code:
        # Supprimer l'OTP après vérification réussie
        cache.delete(cache_key)
        return True
    
    return False


def send_email(to_email, subject, template, context):
    """Envoyer un email en utilisant un template"""
    try:
        # Rendu du template HTML
        html_message = render_to_string(f'emails/{template}.html', context)
        
        # Version texte simple
        text_message = render_to_string(f'emails/{template}.txt', context)
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email sent to {to_email} - Subject: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def generate_secure_token(length=32):
    """Générer un token sécurisé"""
    return secrets.token_urlsafe(length)


def validate_iban(iban):
    """Valider un IBAN tunisien"""
    # Supprimer les espaces
    iban = iban.replace(' ', '').upper()
    
    # Vérifier le format tunisien (TN + 24 caractères)
    if not iban.startswith('TN') or len(iban) != 24:
        return False
    
    # Vérifier que les caractères après TN sont des chiffres
    if not iban[2:].isdigit():
        return False
    
    return True


def sanitize_input(text):
    """Nettoyer les entrées utilisateur pour éviter les injections"""
    if not text:
        return text
    
    # Supprimer les caractères dangereux
    dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/', 'script']
    cleaned_text = text
    
    for char in dangerous_chars:
        cleaned_text = cleaned_text.replace(char, '')
    
    return cleaned_text.strip()


def format_amount(amount, currency='TND'):
    """Formater un montant avec la devise"""
    return f"{amount:.2f} {currency}"


def mask_iban(iban):
    """Masquer partiellement un IBAN pour l'affichage"""
    if len(iban) < 8:
        return iban
    
    return f"{iban[:4]}{'*' * (len(iban) - 8)}{iban[-4:]}"


def validate_transfer_amount(amount, account_balance, max_amount=None):
    """Valider un montant de transfert"""
    errors = []
    
    if amount <= 0:
        errors.append("Amount must be greater than zero")
    
    if amount > account_balance:
        errors.append("Insufficient funds")
    
    if max_amount and amount > max_amount:
        errors.append(f"Amount exceeds maximum transfer limit of {format_amount(max_amount)}")
    
    return len(errors) == 0, errors

def create_user_bank_account(user, account_type='checking', initial_balance=0):
    """
    Crée un compte bancaire unique pour un utilisateur.
    """
    try:
        account = BankAccount.objects.create(
            user=user,
            name=f"{user.name} - {account_type.capitalize()}",
            iban=BankAccount.generate_iban(),
            account_type=account_type,
            balance=initial_balance,
            status='active'
        )
        logger.info(f"Bank account created for user {user.email}: {account.iban}")
        return account
    except Exception as e:
        logger.error(f"Failed to create bank account for user {user.email}: {str(e)}")
        return None
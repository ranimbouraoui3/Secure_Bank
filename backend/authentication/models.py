import uuid
from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from accounts.models import User  # Import explicite du User personnalisé
from transactions.models import Transaction  # Pour les relations si besoin

class Account(models.Model):
    """
    Bank account belonging to a User.
    Compatible with custom User model from accounts.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auth_accounts')
    account_number = models.CharField(max_length=32, unique=True, db_index=True)
    iban = models.CharField(max_length=64, blank=True, null=True)
    currency = models.CharField(max_length=8, default='TND')
    balance = models.DecimalField(max_digits=20, decimal_places=3, default=Decimal('0.000'))
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['account_number']),
        ]

    def __str__(self):
        return f'{self.account_number} ({self.owner.email})'

    def deposit(self, amount: Decimal):
        if amount <= 0:
            raise ValueError('Deposit amount must be positive')
        if self.status != 'active':
            raise ValueError('Cannot deposit into inactive account')
        with transaction.atomic():
            acc = Account.objects.select_for_update().get(pk=self.pk)
            acc.balance = (acc.balance or Decimal('0.000')) + Decimal(amount)
            acc.save(update_fields=['balance', 'updated_at'])
            return acc.balance

    def withdraw(self, amount: Decimal):
        if amount <= 0:
            raise ValueError('Withdrawal amount must be positive')
        if self.status != 'active':
            raise ValueError('Cannot withdraw from inactive account')
        with transaction.atomic():
            acc = Account.objects.select_for_update().get(pk=self.pk)
            if acc.balance < Decimal(amount):
                raise ValueError('Insufficient funds')
            acc.balance = (acc.balance or Decimal('0.000')) - Decimal(amount)
            acc.save(update_fields=['balance', 'updated_at'])
            return acc.balance


class Beneficiary(models.Model):
    """
    A beneficiary that a user can transfer to.
    Compatible with custom User model and banking transactions.
    """
    VERIFICATION_STATUS = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auth_beneficiaries')
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=64)
    bank_name = models.CharField(max_length=255, blank=True)
    verification_status = models.CharField(max_length=16, choices=VERIFICATION_STATUS, default='unverified')
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Beneficiary'
        verbose_name_plural = 'Beneficiaries'
        ordering = ['-created_at']
        unique_together = ('owner', 'account_number')
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['account_number']),
        ]

    def __str__(self):
        return f'{self.name} ({self.account_number})'

    def mark_verified(self):
        self.verification_status = 'verified'
        self.verified_at = timezone.now()
        self.save(update_fields=['verification_status', 'verified_at'])

    def is_verified(self):
        return self.verification_status == 'verified'


# Optionnel: Méthode pour créer une transaction interne vers un bénéficiaire
def transfer_to_beneficiary(from_account: Account, beneficiary: Beneficiary, amount: Decimal, description=""):
    """
    Effectue un transfert interne ou externe vers un bénéficiaire.
    Crée automatiquement un enregistrement Transaction.
    """
    if not beneficiary.is_verified():
        raise ValueError("Cannot transfer to unverified beneficiary")
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if from_account.balance < amount:
        raise ValueError("Insufficient funds")

    with transaction.atomic():
        # Débit du compte source
        from_account.withdraw(amount)

        # Ici, on peut rechercher si le bénéficiaire a un compte interne
        to_account = Account.objects.filter(account_number=beneficiary.account_number).first()

        # Crédit du compte destinataire si interne
        if to_account and to_account.status == 'active':
            to_account.deposit(amount)

        # Création de la transaction
        txn = Transaction.objects.create(
            from_account=from_account,
            to_account=to_account,
            beneficiary=beneficiary,
            transaction_type='transfer',
            amount=amount,
            currency=from_account.currency,
            description=description,
            reference_number=Transaction.generate_reference_number(),
            status='completed',
            otp_verified=True,  # si nécessaire
            ip_address='127.0.0.1',  # à remplacer par request.META['REMOTE_ADDR']
            user_agent='System'      # à remplacer par request.META['HTTP_USER_AGENT']
        )
        return txn

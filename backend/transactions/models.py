"""
Modèles pour l'application transactions
Gère les transactions bancaires, transactions en attente et limites
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from accounts.models import User, BankAccount, Beneficiary
from decimal import Decimal
import uuid
import secrets


class Transaction(models.Model):
    """
    Modèle de transaction bancaire
    Représente une transaction complétée ou en cours
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('transfer', 'Virement'),
        ('deposit', 'Dépôt'),
        ('withdrawal', 'Retrait'),
    ]
    
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('initiated', 'Initié'),
        ('otp_sent', 'OTP Envoyé'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    # Comptes impliqués
    from_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.PROTECT, 
        related_name='outgoing_transactions',
        help_text="Compte source du virement"
    )
    to_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.PROTECT, 
        related_name='incoming_transactions',
        null=True, 
        blank=True,
        help_text="Compte destination (si interne)"
    )
    beneficiary = models.ForeignKey(
        Beneficiary, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Bénéficiaire du virement"
    )
    
    # Détails de la transaction
    transaction_type = models.CharField(
        max_length=10, 
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="Type de transaction"
    )
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Montant de la transaction"
    )
    currency = models.CharField(
        max_length=3, 
        default='TND',
        help_text="Devise de la transaction"
    )
    description = models.TextField(
        blank=True,
        help_text="Description ou motif de la transaction"
    )
    
    # Référence unique
    reference_number = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text="Numéro de référence unique (ex: TXN-20241203-123456)"
    )
    
    # Statut
    status = models.CharField(
        max_length=15, 
        choices=TRANSACTION_STATUS_CHOICES, 
        default='pending',
        help_text="Statut actuel de la transaction"
    )
    
    # Timestamps
    initiated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date d'initiation de la transaction"
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date de complétion de la transaction"
    )
    
    # Sécurité et audit
    ip_address = models.GenericIPAddressField(
        help_text="Adresse IP de l'utilisateur"
    )
    user_agent = models.TextField(
        help_text="User agent du navigateur"
    )
    otp_verified = models.BooleanField(
        default=False,
        help_text="OTP vérifié avec succès"
    )
    confirmation_email_sent = models.BooleanField(
        default=False,
        help_text="Email de confirmation envoyé"
    )
    
    # Informations supplémentaires
    error_message = models.TextField(
        blank=True,
        help_text="Message d'erreur si la transaction a échoué"
    )
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-initiated_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['-initiated_at']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['status']),
            models.Index(fields=['from_account', '-initiated_at']),
            models.Index(fields=['to_account', '-initiated_at']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.amount} {self.currency} ({self.status})"
    
    @staticmethod
    def generate_reference_number():
        """
        Générer un numéro de référence unique pour la transaction
        Format: TXN-YYYYMMDD-XXXXXX
        Returns:
            str: Numéro de référence unique
        """
        date_str = timezone.now().strftime('%Y%m%d')
        random_part = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        while True:
            reference = f"TXN-{date_str}-{random_part}"
            if not Transaction.objects.filter(reference_number=reference).exists():
                return reference
            random_part = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    def mark_completed(self):
        """Marquer la transaction comme complétée"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def mark_failed(self, error_message=""):
        """
        Marquer la transaction comme échouée
        Args:
            error_message (str): Message d'erreur descriptif
        """
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])
    
    def mark_cancelled(self, reason=""):
        """
        Marquer la transaction comme annulée
        Args:
            reason (str): Raison de l'annulation
        """
        self.status = 'cancelled'
        self.error_message = reason
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Vérifier que le montant est positif
        if self.amount and self.amount <= 0:
            raise ValidationError({'amount': 'Le montant doit être positif'})
        
        # Pour un transfert, un bénéficiaire est requis
        if self.transaction_type == 'transfer' and not self.beneficiary:
            raise ValidationError({'beneficiary': 'Un bénéficiaire est requis pour un virement'})
    
    @property
    def is_completed(self):
        """Vérifier si la transaction est complétée"""
        return self.status == 'completed'
    
    @property
    def is_pending(self):
        """Vérifier si la transaction est en attente"""
        return self.status in ['pending', 'initiated', 'otp_sent']
    
    @property
    def duration(self):
        """Calculer la durée de la transaction"""
        if self.completed_at:
            return self.completed_at - self.initiated_at
        return timezone.now() - self.initiated_at


class PendingTransaction(models.Model):
    """
    Transaction en attente de validation OTP
    Stocke temporairement les détails d'une transaction avant validation
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="Utilisateur initiant la transaction"
    )
    from_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.CASCADE,
        help_text="Compte source"
    )
    beneficiary = models.ForeignKey(
        Beneficiary, 
        on_delete=models.CASCADE,
        help_text="Bénéficiaire de la transaction"
    )
    
    # Détails de la transaction
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        help_text="Montant à transférer"
    )
    description = models.TextField(
        blank=True,
        help_text="Description de la transaction"
    )
    
    # OTP
    otp_code = models.CharField(
        max_length=6,
        help_text="Code OTP généré"
    )
    otp_expires_at = models.DateTimeField(
        help_text="Date d'expiration de l'OTP"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création"
    )
    ip_address = models.GenericIPAddressField(
        help_text="Adresse IP de l'utilisateur"
    )
    user_agent = models.TextField(
        help_text="User agent du navigateur"
    )
    
    # État
    is_consumed = models.BooleanField(
        default=False,
        help_text="OTP déjà utilisé"
    )
    
    class Meta:
        db_table = 'pending_transactions'
        ordering = ['-created_at']
        verbose_name = 'Transaction en Attente'
        verbose_name_plural = 'Transactions en Attente'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['otp_expires_at']),
        ]
    
    def __str__(self):
        return f"Pending: {self.amount} TND to {self.beneficiary.name}"
    
    def is_expired(self):
        """
        Vérifier si l'OTP a expiré
        Returns:
            bool: True si expiré, False sinon
        """
        return timezone.now() > self.otp_expires_at
    
    def verify_otp(self, otp_code):
        """
        Vérifier le code OTP fourni
        Args:
            otp_code (str): Code OTP à vérifier
        Returns:
            bool: True si valide, False sinon
        """
        if self.is_consumed:
            return False
        if self.is_expired():
            return False
        return self.otp_code == otp_code
    
    def consume(self):
        """Marquer l'OTP comme consommé"""
        self.is_consumed = True
        self.save(update_fields=['is_consumed'])
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        if self.amount and self.amount <= 0:
            raise ValidationError({'amount': 'Le montant doit être positif'})


class TransactionLimit(models.Model):
    """
    Limites de transaction par utilisateur
    Gère les limites quotidiennes et par transaction
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='transaction_limit',
        primary_key=True,
        help_text="Utilisateur concerné"
    )
    
    # Limites
    daily_transfer_limit = models.DecimalField(
        max_digits=15, 
        decimal_places=3, 
        default=Decimal('10000.000'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Limite de transfert quotidienne en TND"
    )
    single_transfer_limit = models.DecimalField(
        max_digits=15, 
        decimal_places=3, 
        default=Decimal('5000.000'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Limite par transaction en TND"
    )
    
    # Utilisation actuelle
    daily_transfer_used = models.DecimalField(
        max_digits=15, 
        decimal_places=3, 
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Montant déjà utilisé aujourd'hui"
    )
    last_reset_date = models.DateField(
        auto_now_add=True,
        help_text="Date de dernière réinitialisation"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date de dernière modification"
    )
    
    class Meta:
        db_table = 'transaction_limits'
        verbose_name = 'Limite de Transaction'
        verbose_name_plural = 'Limites de Transaction'
    
    def __str__(self):
        return f"Limits for {self.user.email} - Daily: {self.daily_transfer_used}/{self.daily_transfer_limit}"
    
    def reset_daily_limit(self):
        """
        Réinitialiser la limite quotidienne si nécessaire
        Appelé automatiquement avant chaque vérification
        """
        today = timezone.now().date()
        if self.last_reset_date < today:
            self.daily_transfer_used = Decimal('0.000')
            self.last_reset_date = today
            self.save(update_fields=['daily_transfer_used', 'last_reset_date'])
    
    def can_transfer(self, amount):
        """
        Vérifier si l'utilisateur peut effectuer un transfert
        Args:
            amount (Decimal): Montant à transférer
        Returns:
            tuple: (bool, str) - (Peut transférer, Message d'erreur si False)
        """
        # Réinitialiser la limite quotidienne si nécessaire
        self.reset_daily_limit()
        
        # Vérifier la limite par transaction
        if amount > self.single_transfer_limit:
            return False, f"Le montant dépasse la limite par transaction ({self.single_transfer_limit} TND)"
        
        # Vérifier la limite quotidienne
        if self.daily_transfer_used + amount > self.daily_transfer_limit:
            remaining = self.daily_transfer_limit - self.daily_transfer_used
            return False, f"Limite quotidienne dépassée. Reste disponible: {remaining} TND"
        
        return True, ""
    
    def add_to_daily_used(self, amount):
        """
        Ajouter un montant au total quotidien utilisé
        Args:
            amount (Decimal): Montant à ajouter
        """
        self.daily_transfer_used += amount
        self.save(update_fields=['daily_transfer_used'])
    
    def get_remaining_daily_limit(self):
        """
        Obtenir le montant restant disponible aujourd'hui
        Returns:
            Decimal: Montant restant
        """
        self.reset_daily_limit()
        return self.daily_transfer_limit - self.daily_transfer_used
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        if self.single_transfer_limit > self.daily_transfer_limit:
            raise ValidationError({
                'single_transfer_limit': 'La limite par transaction ne peut pas dépasser la limite quotidienne'
            })


# Signal pour créer automatiquement TransactionLimit lors de la création d'un utilisateur
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_transaction_limit(sender, instance, created, **kwargs):
    """Créer automatiquement les limites de transaction pour un nouvel utilisateur"""
    if created:
        TransactionLimit.objects.get_or_create(user=instance)
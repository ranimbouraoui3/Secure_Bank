"""
Modèles pour l'application accounts
Gère les utilisateurs, comptes bancaires, bénéficiaires et logs d'audit
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import pyotp
import secrets


class User(AbstractUser):
    """Utilisateur personnalisé avec authentification renforcée"""
    
    phone_regex = RegexValidator(
        regex=r'^\+?216\d{8}$',
        message="Le numéro doit être au format tunisien: +216XXXXXXXX ou 216XXXXXXXX"
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    name = models.CharField(max_length=100)
    
    otp_secret = models.CharField(max_length=32, blank=True)
    is_2fa_enabled = models.BooleanField(default=True)
    
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    last_password_change = models.DateTimeField(auto_now_add=True)
    password_reset_token = models.CharField(max_length=100, blank=True)
    password_reset_token_expires = models.DateTimeField(null=True, blank=True)
    
    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('locked', 'Verrouillé'),
        ('closed', 'Fermé'),
    ]
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'phone']

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['email']), models.Index(fields=['phone']), models.Index(fields=['account_status'])]
        
    def __str__(self):
        return f"{self.name} ({self.email})"

    def generate_otp_secret(self):
        if not self.otp_secret:
            self.otp_secret = pyotp.random_base32()
            self.save(update_fields=['otp_secret'])
        return self.otp_secret

    def verify_otp(self, otp_code):
        if not self.otp_secret:
            return False
        totp = pyotp.TOTP(self.otp_secret, interval=300)
        return totp.verify(otp_code, valid_window=1)

    def is_account_locked(self):
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        elif self.account_locked_until and timezone.now() >= self.account_locked_until:
            self.account_locked_until = None
            self.failed_login_attempts = 0
            self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
        return False

    def increment_failed_login(self):
        from django.conf import settings
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            self.account_locked_until = timezone.now() + timezone.timedelta(seconds=settings.ACCOUNT_LOCKOUT_TIME)
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])

    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.lower()


class BankAccount(models.Model):
    """Compte bancaire appartenant à un utilisateur"""
    
    ACCOUNT_TYPE_CHOICES = [('checking', 'Compte Courant'), ('savings', 'Compte Épargne')]
    STATUS_CHOICES = [('active', 'Actif'), ('suspended', 'Suspendu'), ('closed', 'Fermé')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    name = models.CharField(max_length=100, default='Main Account')
    iban = models.CharField(max_length=34, unique=True, db_index=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='checking')
    balance = models.DecimalField(max_digits=15, decimal_places=3, default=0.000, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='TND')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_transaction_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'bank_accounts'
        ordering = ['-created_at']
        verbose_name = 'Compte Bancaire'
        verbose_name_plural = 'Comptes Bancaires'
        indexes = [models.Index(fields=['iban']), models.Index(fields=['user', 'status'])]

    def __str__(self):
        return f"{self.name} - {self.iban} ({self.balance} {self.currency})"

    @staticmethod
    def generate_iban():
        while True:
            account_number = ''.join([str(secrets.randbelow(10)) for _ in range(20)])
            iban = f"TN59{account_number}"
            if not BankAccount.objects.filter(iban=iban).exists():
                return iban

    def can_debit(self, amount):
        return self.status == 'active' and self.balance >= amount

    def debit(self, amount):
        if not self.can_debit(amount):
            raise ValueError("Solde insuffisant ou compte inactif")
        self.balance -= amount
        self.last_transaction_date = timezone.now()
        self.save(update_fields=['balance', 'last_transaction_date', 'updated_at'])

    def credit(self, amount):
        if self.status != 'active':
            raise ValueError("Le compte n'est pas actif")
        self.balance += amount
        self.last_transaction_date = timezone.now()
        self.save(update_fields=['balance', 'last_transaction_date', 'updated_at'])

    def clean(self):
        super().clean()
        if self.iban:
            if not self.iban.startswith('TN'):
                raise ValidationError({'iban': 'L\'IBAN doit commencer par TN'})
            if len(self.iban) != 24:
                raise ValidationError({'iban': 'L\'IBAN tunisien doit contenir 24 caractères'})


class Beneficiary(models.Model):
    """Bénéficiaire pour les virements bancaires"""
    
    BANK_TYPE_CHOICES = [('same', 'Même Banque'), ('national', 'Banque Nationale'), ('international', 'Banque Étrangère')]
    STATUS_CHOICES = [('pending_verification', 'En attente de vérification'), ('verified', 'Vérifié'), ('rejected', 'Rejeté')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_beneficiaries')
    name = models.CharField(max_length=100)
    iban = models.CharField(max_length=34)
    bank_name = models.CharField(max_length=100)
    bank_type = models.CharField(max_length=15, choices=BANK_TYPE_CHOICES, default='same')
    swift_code = models.CharField(max_length=11, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending_verification')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'beneficiaries'
        unique_together = ['owner', 'iban']
        ordering = ['name']
        verbose_name = 'Bénéficiaire'
        verbose_name_plural = 'Bénéficiaires'
        indexes = [models.Index(fields=['owner', 'status']), models.Index(fields=['iban'])]

    def __str__(self):
        return f"{self.name} - {self.iban}"

    def clean(self):
        super().clean()
        if self.iban:
            self.iban = self.iban.replace(' ', '').upper()
            if self.bank_type == 'international' and not self.swift_code:
                raise ValidationError({'swift_code': 'Le code SWIFT est requis pour les virements internationaux'})


class AuditLog(models.Model):
    """Journal d'audit pour les actions utilisateur"""
    
    ACTION_TYPE_CHOICES = [
        ('login','Connexion'), ('logout','Déconnexion'), ('failed_login','Tentative de connexion échouée'),
        ('password_change','Changement de mot de passe'), ('password_reset','Réinitialisation de mot de passe'),
        ('profile_update','Mise à jour du profil'), ('transfer_initiated','Virement initié'),
        ('transfer_completed','Virement complété'), ('transfer_failed','Virement échoué'),
        ('transfer_cancelled','Virement annulé'), ('beneficiary_added','Bénéficiaire ajouté'),
        ('beneficiary_updated','Bénéficiaire modifié'), ('beneficiary_deleted','Bénéficiaire supprimé'),
        ('account_locked','Compte verrouillé'), ('account_unlocked','Compte déverrouillé'),
        ('suspicious_activity','Activité suspecte'), ('rate_limit_exceeded','Limite de taux dépassée')
    ]
    
    STATUS_CHOICES = [('success','Succès'), ('failed','Échec'), ('warning','Avertissement')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        verbose_name = "Journal d'Audit"
        verbose_name_plural = "Journaux d'Audit"
        indexes = [models.Index(fields=['-timestamp']), models.Index(fields=['user','action']), models.Index(fields=['action','status']), models.Index(fields=['ip_address'])]

    def __str__(self):
        user_email = self.user.email if self.user else 'Unknown'
        return f"{self.action} - {user_email} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def log_action(cls, user, action, status, ip_address, user_agent, description="", amount=None):
        return cls.objects.create(
            user=user,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
            amount=amount
        )

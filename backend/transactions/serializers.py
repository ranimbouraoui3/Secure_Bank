# transactions/serializers.py

from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'from_account', 'to_account', 'beneficiary',
            'transaction_type', 'amount', 'currency', 'description',
            'reference_number', 'status', 'initiated_at', 'completed_at',
            'ip_address', 'user_agent', 'otp_verified', 'confirmation_email_sent', 'error_message'
        ]
        read_only_fields = ['id', 'reference_number', 'status', 'initiated_at', 'completed_at', 'otp_verified', 'confirmation_email_sent']

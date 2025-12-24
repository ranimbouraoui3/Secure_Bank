from rest_framework import serializers
from accounts.models import User, BankAccount, Beneficiary, AuditLog
from django.contrib.auth import authenticate

# ==================== USER SERIALIZERS ====================

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hash password
        user.save()
        # Optional: generate OTP secret if 2FA enabled
        if getattr(user, 'is_2fa_enabled', False):
            user.generate_otp_secret()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer (for displaying user info)"""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'account_status', 'is_2fa_enabled']


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if getattr(user, 'is_account_locked', lambda: False)():
            raise serializers.ValidationError("Account is locked due to failed login attempts")
        attrs['user'] = user
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone', 'email']
        extra_kwargs = {
            'email': {'required': True},
            'name': {'required': True},
            'phone': {'required': True},
        }

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


# ==================== BANK ACCOUNT SERIALIZER ====================

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id', 'user', 'name', 'iban', 'account_type',
            'balance', 'currency', 'status', 'created_at', 'updated_at', 'last_transaction_date'
        ]
        read_only_fields = ['id', 'user', 'balance', 'created_at', 'updated_at', 'last_transaction_date']


# ==================== BENEFICIARY SERIALIZER ====================

class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = [
            'id', 'owner', 'name', 'iban', 'bank_name', 'bank_type',
            'swift_code', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)


# ==================== AUDIT LOG SERIALIZER ====================

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'action', 'status', 'description',
            'amount', 'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = fields

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None


# ==================== PASSWORD CHANGE SERIALIZER ====================

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, min_length=8)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("New password must be at least 8 characters long")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

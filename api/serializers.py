from rest_framework import serializers
from .models import User, Subscription, Restaurant, BillTransaction, Wallet, WalletTransaction, UserPoints, PointsTransaction, Review
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from fcm_django.models import FCMDevice


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone', 'governorate', 'is_student', 'student_id_card']

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            governorate=validated_data['governorate'],
            is_student=validated_data['is_student'],
            student_id_card=validated_data.get('student_id_card')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['transaction_id', 'date', 'pass_id', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
class BillTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillTransaction
        fields = '__all__'
        read_only_fields = ['user', 'status', 'qr_code', 'time', 'used']

class OnlinePaymentRequestSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    password = serializers.CharField()

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['password']):
            raise serializers.ValidationError("Incorrect password.")
        return data
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'
        read_only_fields = ['wallet', 'status']
class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = ['points']

class PointsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsTransaction
        fields = '__all__'
        read_only_fields = ['user', 'timestamp']
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'restaurant_reply']
class DeviceRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['registration_id', 'type']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, filters, status
from .serializers import UserRegisterSerializer, ReviewSerializer, SubscriptionSerializer, RestaurantSerializer, OnlinePaymentRequestSerializer, BillTransactionSerializer, WalletSerializer, WalletTransactionSerializer, DeviceRegisterSerializer
from .models import User, Subscription, Restaurant, BillTransaction, Wallet, WalletTransaction, UserPoints, PointsTransaction, UserPoints, PointsTransaction, Review
from django.utils import timezone
from datetime import timedelta
from rest_framework.parsers import JSONParser
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from fcm_django.models import FCMDevice

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
class SubscriptionCreateView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['type', 'location']
    ordering_fields = ['rating']

class RestaurantDetailView(generics.RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    lookup_field = 'id'
class OnlinePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(request_body=OnlinePaymentRequestSerializer)
    def post(self, request):
        serializer = OnlinePaymentRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            data = serializer.validated_data

            restaurant = Restaurant.objects.get(id=data['restaurant_id'])
            transaction = BillTransaction.objects.create(
                user=request.user,
                restaurant=restaurant,
                amount=data['amount'],
                method='wallet',
                status='success',
            )

            # ✅ Earn points (1 point per 3000 SYP)
            points = int(data['amount'] // 3000)
            if points > 0:
                up, _ = UserPoints.objects.get_or_create(user=request.user)
                up.points += points
                up.save()

                PointsTransaction.objects.create(
                    user=request.user,
                    transaction_type='earn',
                    points=points,
                    description=f"Earned {points} pts for spending {data['amount']} SYP"
                )

            serialized = BillTransactionSerializer(transaction)
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiscountQRView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        rest_id = request.data.get('restaurant_id')
        restaurant = Restaurant.objects.get(id=rest_id)
        txn = BillTransaction.objects.create(
            user=request.user,
            restaurant=restaurant,
            method='discount_only',
            status='success',
            is_discount_only=True
        )
        return Response(BillTransactionSerializer(txn).data)
class WalletBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

class WalletRechargeView(generics.CreateAPIView):
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        wallet = Wallet.objects.get(user=self.request.user)  # Wallet guaranteed hoga (signals se)
        amount = serializer.validated_data['amount']
        transaction = serializer.save(wallet=wallet, transaction_type='recharge', status='success')

        # Update wallet balance
        wallet.balance += amount
        wallet.save()

class WalletTransactionHistoryView(generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WalletTransaction.objects.filter(wallet__user=self.request.user).order_by('-timestamp')
class UserPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        up = UserPoints.objects.get(user=request.user)
        return Response({'points': up.points})

class RedeemPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        up = UserPoints.objects.get(user=user)
        if up.points < 100:
            return Response({"error": "Not enough points to redeem."}, status=400)

        # Deduct points
        up.points -= 100
        up.save()

        # Add 10,000 SYP to wallet
        wallet = Wallet.objects.get(user=user)
        wallet.balance += 10000
        wallet.save()

        # Log both transactions
        PointsTransaction.objects.create(
            user=user,
            transaction_type='redeem',
            points=100,
            description="Redeemed 100 points for 10,000 SYP"
        )

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=10000,
            transaction_type='recharge',
            method='system',
            status='success'
        )

        return Response({"message": "Points redeemed successfully. 10,000 SYP added to wallet."})
class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        transaction_id = self.request.data.get("transaction")

        try:
            txn = BillTransaction.objects.get(id=transaction_id, user=user)
        except BillTransaction.DoesNotExist:
            raise ValidationError("Invalid or unauthorized transaction.")

        # Ensure it's within 24 hours
        if (timezone.now() - txn.time).total_seconds() > 86400:
            raise ValidationError("Review time window expired (24h).")

        # Prevent duplicate review on same transaction
        if Review.objects.filter(user=user, transaction=txn).exists():
            raise ValidationError("You already reviewed this visit.")

        serializer.save(user=user, restaurant=txn.restaurant, transaction=txn)

class RestaurantReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return Review.objects.filter(restaurant__id=restaurant_id).order_by('-created_at')
class DeviceRegisterView(generics.CreateAPIView):
    serializer_class = DeviceRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]
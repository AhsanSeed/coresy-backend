from django.urls import path
from .views import RegisterView, SubscriptionCreateView, SubscriptionListView, RestaurantListView, RestaurantDetailView, DiscountQRView, WalletBalanceView, WalletRechargeView, WalletTransactionHistoryView, UserPointsView, RedeemPointsView, CreateReviewView, RestaurantReviewListView, DeviceRegisterView

from .views import OnlinePaymentView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('subscriptions/create/', SubscriptionCreateView.as_view(), name='subscription-create'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
    path('restaurants/', RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurants/<int:id>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('payment/online/', OnlinePaymentView.as_view(), name='online-payment'),
    path('payment/discount/', DiscountQRView.as_view(), name='discount-qr'),
    path('wallet/balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('wallet/recharge/', WalletRechargeView.as_view(), name='wallet-recharge'),
    path('wallet/history/', WalletTransactionHistoryView.as_view(), name='wallet-history'),
    path('points/', UserPointsView.as_view(), name='points'),
    path('points/redeem/', RedeemPointsView.as_view(), name='points-redeem'),
    path('reviews/create/', CreateReviewView.as_view(), name='review-create'),
    path('reviews/<int:restaurant_id>/', RestaurantReviewListView.as_view(), name='restaurant-reviews'),
    path('notifications/register-device/', DeviceRegisterView.as_view(), name='register-device'),
]

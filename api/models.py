from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils.timezone import now
from django.utils import timezone
from django.core.exceptions import ValidationError
import qrcode
from io import BytesIO
from django.core.files import File

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    governorate = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    student_id_card = models.ImageField(upload_to='student_ids/', null=True, blank=True)
    email_verified = models.BooleanField(default=False)
class Subscription(models.Model):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('non-student', 'Non-Student'),
    )

    PAYMENT_METHODS = (
        ('wallet', 'In-App Wallet'),
        ('external', 'External API'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=now)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    pass_id = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pass_id:
            last_id = Subscription.objects.count() + 1
            self.pass_id = f"DM-{last_id:06d}"
        super().save(*args, **kwargs)
class Restaurant(models.Model):
    TYPE_CHOICES = (
        ('cafe', 'Cafe'),
        ('bar', 'Bar'),
        ('restaurant', 'Restaurant'),
        ('fastfood', 'Fast Food'),
    )

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=100)
    rating = models.FloatField(default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField()
    discount_percent = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name
class BillTransaction(models.Model):
    PAYMENT_METHODS = (
        ('wallet', 'Wallet'),
        ('external', 'External'),
        ('discount_only', 'Discount Only'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    time = models.DateTimeField(default=timezone.now)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_discount_only = models.BooleanField(default=False)
    used = models.BooleanField(default=False)

    def generate_qr(self):
        data = f"{self.user.id}-{self.restaurant.id}-{timezone.now().timestamp()}"
        qr_img = qrcode.make(data)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        self.qr_code.save(f"qr_{self.id}.png", File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr()
        super().save(*args, **kwargs)
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} Wallet"

class WalletTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('recharge', 'Recharge'),
        ('spend', 'Spend'),
    )
    METHOD_CHOICES = (
        ('chamcash', 'Cham Cash'),
        ('syriatel', 'Syriatel'),
        ('ecash', 'eCash'),
        ('mtn', 'MTN'),
        ('card', 'Prepaid Card'),
        ('system', 'System Use'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=[('success', 'Success'), ('failed', 'Failed')], default='success')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - {self.amount}"
class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} pts"

class PointsTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('earn', 'Earn'),
        ('redeem', 'Redeem'),
        ('bonus', 'Bonus'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.points} pts"
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    transaction = models.ForeignKey(BillTransaction, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    restaurant_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name} ({self.rating}★)"

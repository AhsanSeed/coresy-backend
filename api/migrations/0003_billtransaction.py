# Generated by Django 5.0.6 on 2025-07-13 13:53

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_restaurant'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('method', models.CharField(choices=[('wallet', 'Wallet'), ('external', 'External'), ('discount_only', 'Discount Only')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=10)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
                ('is_discount_only', models.BooleanField(default=False)),
                ('used', models.BooleanField(default=False)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.restaurant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

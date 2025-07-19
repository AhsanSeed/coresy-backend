# CoreSY Backend (Django)

A full-featured restaurant subscription & billing system built with Django REST Framework and PostgreSQL.

## 🔧 Features

- 🔐 User Authentication (JWT)
- 🏬 Restaurant Listing
- 📦 Subscription Module (Auto Scheduler for expiry reminders)
- 💳 Bill Payment via QR
- 💰 Wallet System (Recharge, Balance, History)
- 🎁 Points & Rewards System
- ⭐ Reviews
- 🔔 Firebase Notifications

## 🚀 Technologies Used

- Python Django + DRF
- PostgreSQL
- Swagger API Docs
- Firebase
- Git + GitHub

## 📁 API Docs

Swagger UI available at:  
`/swagger/`

## 📦 Setup Instructions

```bash
git clone https://github.com/AhsanSeed/coresy-backend.git
cd coresy-backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

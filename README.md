# MFA Auth Project

A full **Multi-Factor Authentication (MFA) system** built with **Django + Django REST Framework** for the backend and **React (Vite)** for the frontend. Uses **MySQL** for persistent storage, **Redis** for OTP/session caching, and **PyOTP** for TOTP-based MFA. JWT authentication is used with access and refresh tokens.

---

## **Tech Stack**

- Backend: Django, Django REST Framework
- Frontend: React + Vite
- Database: MySQL
- Caching: Redis
- Authentication: JWT + TOTP MFA
- Email: SMTP for OTP

---

## **Project Structure**

mfa-auth-project/
├── backend/ # Django backend
├── frontend/ # React frontend
├── .gitignore
└── README.md

yaml
Copy code

---

## **Backend Setup**

1. Create a virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Configure .env with your environment variables (DB, Redis, email, JWT secrets).

Apply migrations:

bash
Copy code
python manage.py makemigrations
python manage.py migrate
Create a superuser (optional):

bash
Copy code
python manage.py createsuperuser
Run the Django server:

bash
Copy code
python manage.py runserver
Backend will run at: http://127.0.0.1:8015/

Frontend Setup
Navigate to frontend folder:

bash
Copy code
cd ../frontend
Install dependencies:

bash
Copy code
npm install
Start frontend development server:

bash
Copy code
npm run dev
Frontend will run at: http://localhost:5173/

Usage
Register: Navigate to /register, create a new user.

Login: Navigate to /login and authenticate with email/password.

MFA Setup: After login, visit /mfa-setup to see QR code for TOTP. Scan it using an authenticator app (e.g., Google Authenticator).

MFA Verify: Navigate to /mfa-verify and enter TOTP from your app. You can also request an OTP via email.

Dashboard: Once MFA is verified, access the protected /dashboard.

Logout: Click logout to revoke tokens and clear session.

Notes
Redis is required for OTP/session caching.

MySQL must be running for persistent user storage.

JWT tokens are stored in localStorage for simplicity; for production, consider httpOnly cookies.

Rate-limiting and production-grade security are suggested to be added for real deployment.

Commands Summary
Backend

bash

cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
Frontend

bash

cd frontend
npm install
npm run dev
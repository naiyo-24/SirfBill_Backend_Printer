# Manju Medicine Backend

This is the backend API for the Manju Medicine platform. It is built using **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **Strawberry GraphQL**. It serves both the Patient app (mobile) and the Admin Dashboard.

## 🚀 Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (with Alembic for migrations)
- **GraphQL:** Strawberry GraphQL
- **Authentication:** JWT & APITXT for OTPs
- **File Uploads:** Local storage (`/uploads`)

## 📂 Project Structure

```text
manju_medicine_backend/
├── main.py                     # Entry point of the FastAPI application
├── dependencies.py             # Dependency injection (e.g., get_db, auth logic)
├── database.db                 # SQLite (Legacy/Local dev if not using Postgres)
│
├── alembic/                    # Database migrations (Alembic)
│   ├── env.py                  # Alembic environment config
│   └── versions/               # Generated migration scripts
│
├── crud/                       # Database operations (Create, Read, Update, Delete)
│   ├── appointment.py          # CRUD for appointments
│   ├── doctor.py               # CRUD for doctors
│   ├── lab_booking.py          # CRUD for lab bookings
│   ├── user.py                 # CRUD for users
│   └── ...
│
├── graphql_api/                # GraphQL implementation (Strawberry)
│   ├── schema.py               # Main GraphQL schema aggregator
│   ├── queries/                # GraphQL Read operations (e.g., getAdminAppointments)
│   ├── mutations/              # GraphQL Write operations
│   └── types/                  # GraphQL Object Types (e.g., DoctorType, UserType)
│
├── models/                     # SQLAlchemy ORM Models (Database Schema)
│   ├── database.py             # SQLAlchemy engine and sessionmaker setup
│   ├── enums.py                # Enums (e.g., BookingStatus)
│   ├── appointment.py
│   ├── doctor.py
│   ├── lab_booking.py
│   ├── user.py
│   └── ...
│
├── routes/                     # REST API Endpoints (FastAPI Routers)
│   ├── auth.py                 # JWT login and APITXT OTP verification
│   ├── appointment.py          # REST routes for appointments (e.g., status updates)
│   ├── doctor.py               # REST routes for doctors
│   ├── lab_booking.py          # REST routes for lab bookings
│   └── user.py                 # REST routes for user creation
│
├── schemas/                    # Pydantic Models (Data Validation & Serialization)
│   ├── auth.py                 # Validation for login/OTP payloads
│   ├── appointment.py          # Validation for appointment payloads
│   ├── doctor.py               # Validation for doctor payloads
│   └── ...
│
└── uploads/                    # Local storage for uploaded media
    ├── banners/
    ├── doctors/                # Doctor profile images
    ├── prescriptions/          # Uploaded prescriptions & stamped PDFs
    ├── profiles/
    ├── reports/                # Uploaded lab reports
    └── stories/
```

## 🛠️ Key Features
- **Hybrid API Architecture:** Uses REST for mutations, file uploads, and admin actions. Uses GraphQL for complex dashboard reads and data aggregation.
- **Admin Appointments Module:** Supports filtering appointments by strict enum statuses (e.g., `CONFIRMED`, `COMPLETED`).
- **Dynamic Prescription PDF Stamping:** Automatically stamps patient/doctor details onto a base PDF template (`F Dr Pad.pdf`).
- **Role-Based Authentication:** Separate login flows and permissions for `ADMIN` and `USER` roles.

## 🏃‍♂️ How to Run Locally

1. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the `.env` file with your PostgreSQL credentials.
4. Run migrations to build the database:
   ```bash
   alembic upgrade head
   ```
5. Start the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

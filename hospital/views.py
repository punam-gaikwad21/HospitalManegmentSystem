from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from datetime import datetime

from .models import Doctor, Patient, Appointment


def index(request):
    doctors = Doctor.objects.all()
    return render(request, 'index.html', {'doctors': doctors})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'doctor'):
                return redirect('doctor_dashboard')
            elif hasattr(user, 'patient'):
                return redirect('patient_dashboard')
            else:
                return redirect('index')
        else:
            messages.error(request, "Invalid username or password ")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('index')


def register_patient(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        age = request.POST.get('age')

        if password != confirm_password:
            messages.error(request, "Passwords do not match ")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists ")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists ")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        Patient.objects.create(user=user, age=age)

        messages.success(request, "Account created successfully ✅")
        return redirect('login')

    return render(request, 'register.html')


# ------------------ BOOK APPOINTMENT ------------------
@login_required(login_url='login')
def book_appointment(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Only patients can book appointment ")
        return redirect('login')

    if request.method == "POST":
        try:
            doctor_id = request.POST.get('doctor')
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            department = request.POST.get('department')

            # validation
            if not all([doctor_id, date_str, time_str, department]):
                messages.error(request, "All fields are required ")
                return redirect('patient_dashboard')

            doctor = get_object_or_404(Doctor, id=doctor_id)
            patient = request.user.patient

            # safe parsing
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            time = datetime.strptime(time_str, "%H:%M").time()

            # duplicate check
            if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
                messages.error(request, "This slot is already booked ")
                return redirect('patient_dashboard')

            # token logic
            token = Appointment.objects.filter(doctor=doctor, date=date).count() + 1

            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                time=time,
                department=department,
                token_number=token,
                status="Pending"
            )

            messages.success(request, "Appointment booked successfully ")

        except ValueError:
            messages.error(request, "Invalid date or time format ")
        except Exception:
            messages.error(request, "Something went wrong while booking ")

        return redirect('patient_dashboard')

    return redirect('index')


# ------------------ PATIENT DASHBOARD ------------------
@login_required(login_url='login')
def patient_dashboard(request):
    if not hasattr(request.user, 'patient'):
        return redirect('login')

    appointments = Appointment.objects.filter(
        patient=request.user.patient
    ).order_by('-date')

    return render(request, 'patient_dashboard.html', {
        'appointments': appointments
    })


# ------------------ DOCTOR DASHBOARD ------------------
@login_required(login_url='login')
def doctor_dashboard(request):
    if not hasattr(request.user, 'doctor'):
        return redirect('login')

    appointments = Appointment.objects.filter(
        doctor=request.user.doctor
    ).order_by('-date')

    return render(request, 'doctor_dashboard.html', {
        'appointments': appointments
    })


# ------------------ COMPLETE APPOINTMENT ------------------
@login_required(login_url='login')
def complete_appointment(request, id):
    if not hasattr(request.user, 'doctor'):
        return redirect('login')

    appointment = get_object_or_404(Appointment, id=id)

    try:
        if appointment.doctor.user != request.user:
            messages.error(request, "Not authorized ❌")
            return redirect('doctor_dashboard')

        appointment.status = "Completed"
        appointment.save()
        messages.success(request, "Marked as completed ✅")

    except Exception:
        messages.error(request, "Error updating appointment ❌")

    return redirect('doctor_dashboard')


# ------------------ CANCEL APPOINTMENT ------------------
@login_required(login_url='login')
def cancel_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)

    if appointment.patient.user != request.user:
        return redirect('patient_dashboard')

    appointment.status = "Cancelled"
    appointment.save()

    messages.warning(request, "Appointment cancelled ❌")
    return redirect('patient_dashboard')


# ------------------ ADMIN DASHBOARD ------------------
@staff_member_required(login_url='login')
def admin_dashboard(request):
    patients = Patient.objects.all().order_by('-id')
    doctors = Doctor.objects.all().order_by('-id')
    appointments = Appointment.objects.all().order_by('-date')

    context = {
        'patients': patients,
        'doctors': doctors,
        'appointments': appointments,
        'total_patients': patients.count(),
        'total_doctors': doctors.count(),
        'total_appointments': appointments.count(),
        'pending': appointments.filter(status="Pending").count(),
    }

    return render(request, 'admin_dashboard.html', context)


# ------------------ DELETE PATIENT ------------------
@staff_member_required(login_url='login')
def delete_patient(request, id):
    try:
        patient = get_object_or_404(Patient, id=id)
        patient.delete()
        messages.success(request, "Patient deleted successfully ✅")
    except Exception:
        messages.error(request, "Error deleting patient ❌")

    return redirect('admin_dashboard')


# ------------------ DELETE DOCTOR ------------------
@staff_member_required(login_url='login')
def delete_doctor(request, id):
    try:
        doctor = get_object_or_404(Doctor, id=id)
        doctor.delete()
        messages.success(request, "Doctor deleted successfully ✅")
    except Exception:
        messages.error(request, "Error deleting doctor ❌")

    return redirect('admin_dashboard')


# ------------------ ADD PATIENT ------------------
@staff_member_required(login_url='login')
def add_patient(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        age = request.POST.get('age')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists ❌")
            return redirect('add_patient')

        user = User.objects.create_user(username=username, password=password)
        Patient.objects.create(user=user, age=age)

        messages.success(request, "Patient added successfully ✅")
        return redirect('admin_dashboard')

    return render(request, 'add_patient.html')


# ------------------ ADD DOCTOR ------------------
@staff_member_required(login_url='login')
def add_doctor(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        specialization = request.POST.get("specialization")
        image = request.FILES.get("image")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists ❌")
            return redirect('add_doctor')

        user = User.objects.create_user(username=username, password=password)

        Doctor.objects.create(
            user=user,
            specialization=specialization,
            image=image
        )

        messages.success(request, "Doctor added successfully ✅")
        return redirect('add_doctor')

    return render(request, 'add_doctor.html')
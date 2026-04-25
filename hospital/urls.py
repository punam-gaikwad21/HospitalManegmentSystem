from django.urls import path
from . import views

urlpatterns = [

    # 🔹 HOME
    path('', views.index, name='index'),

    # 🔹 AUTH
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_patient, name='register'),

    # 🔹 DASHBOARDS
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # 🔹 APPOINTMENTS
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointments/<int:id>/cancel/', views.cancel_appointment, name='cancel_appointment'),

    # 🔹 ADMIN ACTIONS
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('patients/add/', views.add_patient, name='add_patient'),

    path('patients/<int:id>/delete/', views.delete_patient, name='delete_patient'),
    path('doctors/<int:id>/delete/', views.delete_doctor, name='delete_doctor'),
]
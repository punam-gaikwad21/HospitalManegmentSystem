from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


# ------------------ DOCTOR ------------------
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to='doctors/',
        null=True,
        blank=True,
        default='doctors/default.png'   
    )

    def __str__(self):
        return self.user.username


# ------------------ PATIENT ------------------
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return self.user.username


# ------------------ APPOINTMENT ------------------
class Appointment(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    date = models.DateField()
    time = models.TimeField()

    department = models.CharField(max_length=100)

    token_number = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']

        #  prevent duplicate booking
        unique_together = ['doctor', 'date', 'time']

        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['doctor']),
        ]

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.date} {self.time})"
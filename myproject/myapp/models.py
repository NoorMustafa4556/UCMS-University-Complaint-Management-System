from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# -----------------------------------------
# 1. PROFILE MODEL
# -----------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='default.jpg', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'


# -----------------------------------------
# 2. COMPLAINT MODEL (FINAL MERGED VERSION)
# -----------------------------------------
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Sent', 'Sent'),
        ('Pending', 'Pending'),
        ('In Process', 'In Process'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]

    DEPARTMENT_CHOICES = [
        ('CS', 'Computer Science'),
        ('IT', 'Information Technology'),
        ('SE', 'Software Engineering'),
        ('Management', 'Management'),
        ('Other', 'Other'),
    ]

    CATEGORY_CHOICES = [
        ('Academic', 'Academic'),
        ('Hostel', 'Hostel'),
        ('Transport', 'Transport'),
        ('Cafeteria', 'Cafeteria'),
        ('Other', 'Other'),
    ]

    # Foreign Key to User (Student)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Form Fields
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=50)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    complaint_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Academic')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.ImageField(upload_to='complaints/', blank=True, null=True)

    # Admin Section
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Sent')
    admin_remark = models.TextField(blank=True, null=True)   # ← New Field Added

    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


# -----------------------------------------
# 3. AUTO CREATE & SAVE PROFILE SIGNALS
# -----------------------------------------
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


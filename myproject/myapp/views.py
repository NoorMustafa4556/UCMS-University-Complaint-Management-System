from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from .models import Complaint, Profile


# --------------------------------------------------------
# 🏠 HOME PAGE
# --------------------------------------------------------
def home_view(request):
    return render(request, 'events/home.html')


# --------------------------------------------------------
# 🔐 AUTHENTICATION
# --------------------------------------------------------
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Handle Profile Image Upload
            if request.FILES.get('profile_image'):
                # Ensure profile exists (it is created by signal, but safe to fetch)
                # We access the related profile object directly
                # Note: signals create the profile, so we just update it
                user.profile.image = request.FILES['profile_image']
                user.profile.save()

            messages.success(request, 'Account created! Please log in.')
            return redirect('login')

    return render(request, 'events/user_side/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('admin-dashboard')
            return redirect('student-dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'events/user_side/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# --------------------------------------------------------
# 👤 PROFILE + PASSWORD UPDATE (MERGED VERSION)
# --------------------------------------------------------
@login_required
def profile_view(request):
    # Ensure profile object exists
    Profile.objects.get_or_create(user=request.user)
    user = request.user

    # -------------------------------------------------
    # UPDATE PROFILE DETAILS
    # -------------------------------------------------
    if request.method == 'POST' and 'update_profile' in request.POST:

        user.first_name = request.POST.get('full_name')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')

        # Image Update
        if request.FILES.get('profile_image'):
            user.profile.image = request.FILES.get('profile_image')
            user.profile.save()

        user.save()
        user.save()
        messages.success(request, 'Profile updated successfully!')
        
        if user.is_superuser:
            return redirect('admin-dashboard')
        return redirect('student-dashboard')

    # -------------------------------------------------
    # PASSWORD CHANGE WITH 3-ATTEMPT SECURITY
    # -------------------------------------------------
    if request.method == 'POST' and 'change_password' in request.POST:

        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        attempts = request.session.get('pwd_attempts', 0)

        if attempts >= 3:
            messages.error(request, "Security Alert: 3 failed attempts. Logout and try again later.")
            return redirect('profile')

        if not user.check_password(old_pass):
            attempts += 1
            request.session['pwd_attempts'] = attempts
            remaining = 3 - attempts
            messages.error(request, f"Old password incorrect! {remaining} attempts left.")
            return redirect('profile')

        if new_pass != confirm_pass:
            messages.error(request, "New password and confirm password do not match!")
            return redirect('profile')

        # Change Password
        user.set_password(new_pass)
        user.save()
        update_session_auth_hash(request, user)

        # Reset attempts
        request.session['pwd_attempts'] = 0

        messages.success(request, "Password changed successfully!")
        
        if user.is_superuser:
            return redirect('admin-dashboard')
        return redirect('student-dashboard')

    return render(request, 'events/profile.html')


# --------------------------------------------------------
# 🎓 STUDENT DASHBOARD + COMPLAINT SYSTEM
# --------------------------------------------------------
@login_required
def student_dashboard(request):
    # Only show Active complaints (Sent, Pending, In Process)
    my_complaints = Complaint.objects.filter(user=request.user).exclude(status__in=['Resolved', 'Rejected']).order_by('-created_at')
    return render(request, 'events/student_dashboard.html', {'complaints': my_complaints})


@login_required
def complaint_history(request):
    # Only show Closed complaints (Resolved, Rejected)
    history_complaints = Complaint.objects.filter(user=request.user, status__in=['Resolved', 'Rejected']).order_by('-created_at')
    return render(request, 'events/complaint_history.html', {'complaints': history_complaints})


@login_required
def register_complaint(request):
    if request.method == 'POST':
        Complaint.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            roll_number=request.POST.get('roll_number'),
            department=request.POST.get('department'),
            complaint_category=request.POST.get('category'),
            subject=request.POST.get('subject'),
            description=request.POST.get('description'),
            attachment=request.FILES.get('attachment')
        )

        messages.success(request, 'Complaint submitted successfully!')
        return redirect('student-dashboard')

    return render(request, 'events/register_complaint.html')


# --------------------------------------------------------
# 🛡️ ADMIN PANEL + FILTERS + REMARK SYSTEM
# --------------------------------------------------------
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('student-dashboard')

    status_filter = request.GET.get('status')
    dept_filter = request.GET.get('dept')

    complaints = Complaint.objects.all().order_by('-created_at')

    if status_filter:
        complaints = complaints.filter(status=status_filter)

    if dept_filter:
        complaints = complaints.filter(department=dept_filter)

    context = {
        'complaints': complaints,
        'total': Complaint.objects.count(),
        'pending': Complaint.objects.filter(status='Pending').count(),
        'resolved': Complaint.objects.filter(status='Resolved').count(),
        'process': Complaint.objects.filter(status='In Process').count(),
    }

    return render(request, 'events/admin_dashboard.html', context)


@login_required
def update_complaint_status(request, id):
    if not request.user.is_superuser:
        return redirect('home')

    complaint = get_object_or_404(Complaint, id=id)

    if request.method == 'POST':
        complaint.status = request.POST.get('status')
        complaint.admin_remark = request.POST.get('admin_remark')
        complaint.save()

        messages.success(request, 'Status & remark updated!')
        return redirect('admin-dashboard')

    return render(request, 'events/complaint_detail.html', {'c': complaint})


@login_required
def complaint_list(request, status):
    if not request.user.is_superuser:
        return redirect('student-dashboard')

    if status == 'Total':
        complaints = Complaint.objects.all().order_by('-created_at')
        title = "All Complaints"
    else:
        complaints = Complaint.objects.filter(status=status).order_by('-created_at')
        title = f"{status} Complaints"

    context = {
        'complaints': complaints,
        'title': title
    }
    return render(request, 'events/complaint_list.html', context)

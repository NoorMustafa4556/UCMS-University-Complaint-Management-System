from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # ------------------------
    # HOME + AUTH ROUTES
    # ------------------------
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ------------------------
    # PROFILE ROUTE
    # ------------------------
    path('profile/', views.profile_view, name='profile'),

    # ------------------------
    # STUDENT ROUTES
    # ------------------------
    path('dashboard/', views.student_dashboard, name='student-dashboard'),
    path('history/', views.complaint_history, name='complaint-history'),
    path('register-complaint/', views.register_complaint, name='register-complaint'),

    # ------------------------
    # ADMIN ROUTES
    # ------------------------
    path('admin-panel/', views.admin_dashboard, name='admin-dashboard'),
    path('admin-panel/complaints/<str:status>/', views.complaint_list, name='complaint-list'),
    path('complaint/<int:id>/update/', views.update_complaint_status, name='update-status'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

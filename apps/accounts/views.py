import secrets
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .forms import UserRegistrationForm, LoginForm, ProfileUpdateForm, CustomPasswordChangeForm
from .models import User, EmailVerificationToken, PasswordResetToken
from apps.notifications.tasks import send_verification_email


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            _send_verification(user)
            messages.success(request, 'Account created! Please check your email to verify.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            remember_me = form.cleaned_data.get('remember_me', True)
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@require_POST
def user_logout(request):
    logout(request)
    return redirect('core:home')


@login_required
def profile(request):
    from apps.bookings.models import Appointment
    bookings = Appointment.objects.filter(user=request.user).select_related(
        'service', 'stylist'
    ).order_by('-appointment_date')[:10]
    return render(request, 'accounts/profile.html', {'bookings': bookings})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


def verify_email(request, token):
    vt = get_object_or_404(EmailVerificationToken, token=token)
    if not vt.is_valid():
        messages.error(request, 'Verification link has expired.')
        return redirect('accounts:login')
    vt.user.email_verified = True
    vt.user.save(update_fields=['email_verified'])
    vt.delete()
    messages.success(request, 'Email verified successfully! You can now log in.')
    return redirect('accounts:login')


def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').lower()
        try:
            user = User.objects.get(email=email, email_verified=False)
            _send_verification(user)
            messages.success(request, 'Verification email sent.')
        except User.DoesNotExist:
            messages.info(request, 'If that email exists and is unverified, we sent a link.')
    return render(request, 'accounts/resend_verification.html')


def _send_verification(user):
    EmailVerificationToken.objects.filter(user=user).delete()
    token = secrets.token_urlsafe(48)
    EmailVerificationToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(hours=24),
    )
    send_verification_email.delay(user.id, token)

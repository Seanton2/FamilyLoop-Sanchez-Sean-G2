from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from circles.utils import circle_context


@login_required
def dashboard(request):
    if request.user.role == 'ADMIN':
        return redirect('admin_dashboard')
    return redirect('member_dashboard')


@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "You don't have access to that page.")
        return redirect('dashboard')
    return render(request, 'dashboard/admin_dashboard.html')


@login_required
def member_dashboard(request):
    if request.user.role != 'MEMBER':
        messages.error(request, "You don't have access to that page.")
        return redirect('dashboard')
    return render(request, 'dashboard/member_dashboard.html', circle_context(request.user))
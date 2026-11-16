from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import CircleForm
from .models import FamilyMember
from .utils import get_membership


@login_required
def circle_create(request):
    if request.user.role != 'ADMIN':
        messages.error(request, 'Only a Family Administrator can create a circle.')
        return redirect('dashboard')
    if get_membership(request.user):
        messages.error(request, 'You already belong to a family circle.')
        return redirect('circle_detail')

    if request.method == 'POST':
        form = CircleForm(request.POST)
        if form.is_valid():
            circle = form.save(commit=False)
            circle.created_by = request.user  # links the record to the logged-in user
            circle.save()
            FamilyMember.objects.create(
                family_circle=circle,
                user=request.user,
                role='ADMIN',  # the creator automatically becomes the administrator (BR-03)
                joined_at=timezone.now(),
            )
            messages.success(request, f'Your circle "{circle.circle_name}" was created!')
            return redirect('circle_detail')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = CircleForm()
    return render(request, 'circles/circle_form.html', {
        'form': form,
        'heading': 'Create a family circle',
        'button': 'Create circle',
    })


@login_required
def circle_detail(request):
    membership = get_membership(request.user)
    if membership is None:
        if request.user.role == 'ADMIN':
            return redirect('circle_create')
        return redirect('dashboard')
    circle = membership.family_circle
    members = circle.memberships.filter(membership_status='ACTIVE').select_related('user')
    return render(request, 'circles/circle_detail.html', {
        'circle': circle,
        'membership': membership,
        'members': members,
    })

@login_required
def circle_edit(request):
    membership = get_membership(request.user)
    if membership is None or membership.role != 'ADMIN':
        messages.error(request, 'Only the circle administrator can do that.')
        return redirect('dashboard')

    circle = membership.family_circle
    if request.method == 'POST':
        form = CircleForm(request.POST, instance=circle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your circle name was updated.')
            return redirect('circle_detail')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = CircleForm(instance=circle)
    return render(request, 'circles/circle_form.html', {
        'form': form,
        'heading': 'Edit your circle',
        'button': 'Save changes',
    })

@login_required
def circle_delete(request):
    membership = get_membership(request.user)
    if membership is None or membership.role != 'ADMIN':
        messages.error(request, 'Only the circle administrator can do that.')
        return redirect('dashboard')

    if request.method == 'POST':
        circle = membership.family_circle
        name = circle.circle_name
        circle.delete()  # the memberships are deleted with it
        messages.success(request, f'The circle "{name}" was deleted.')
    return redirect('dashboard')
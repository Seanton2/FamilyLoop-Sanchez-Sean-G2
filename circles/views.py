from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CircleForm, JoinCircleForm
from .models import FamilyCircle, FamilyMember
from .utils import get_membership


@login_required
def circle_create(request):
    if request.method == 'POST':
        form = CircleForm(request.POST)
        if form.is_valid():
            circle = form.save(commit=False)
            circle.created_by = request.user
            circle.save()
            FamilyMember.objects.create(
                family_circle=circle,
                user=request.user,
                role='ADMIN',
                joined_at=timezone.now(),
            )
            messages.success(request, f'Your circle "{circle.circle_name}" was created!')
            return redirect('circle_detail_id', circle_id=circle.id)
        messages.error(request, 'Circle name must be at least 3 characters.')
    else:
        form = CircleForm()
    return render(request, 'circles/circle_form.html', {
        'form': form,
        'heading': 'Create a family circle',
        'button': 'Create circle',
    })


@login_required
def circle_detail(request, circle_id=None):
    if circle_id:
        membership = get_object_or_404(
            FamilyMember,
            user=request.user,
            family_circle_id=circle_id,
            membership_status='ACTIVE',
        )
    else:
        membership = get_membership(request.user)

    if membership is None:
        return redirect('circle_join')

    circle = membership.family_circle
    members = circle.memberships.filter(membership_status='ACTIVE').select_related('user')
    return render(request, 'circles/circle_detail.html', {
        'circle': circle,
        'membership': membership,
        'members': members,
    })


@login_required
def circle_edit(request, circle_id=None):
    if circle_id:
        membership = get_object_or_404(
            FamilyMember,
            user=request.user,
            family_circle_id=circle_id,
            membership_status='ACTIVE',
        )
    else:
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
            return redirect('circle_detail_id', circle_id=circle.id)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = CircleForm(instance=circle)
    return render(request, 'circles/circle_form.html', {
        'form': form,
        'heading': 'Edit your circle',
        'button': 'Save changes',
    })


@login_required
def circle_delete(request, circle_id=None):
    if circle_id:
        membership = get_object_or_404(
            FamilyMember,
            user=request.user,
            family_circle_id=circle_id,
            membership_status='ACTIVE',
        )
    else:
        membership = get_membership(request.user)

    if membership is None or membership.role != 'ADMIN':
        messages.error(request, 'Only the circle administrator can do that.')
        return redirect('dashboard')

    if request.method == 'POST':
        circle = membership.family_circle
        name = circle.circle_name
        circle.delete()
        messages.success(request, f'The circle "{name}" was deleted.')
    return redirect('dashboard')


@login_required
def circle_join(request):
    if request.method == 'POST':
        form = JoinCircleForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['invite_code']
            try:
                circle = FamilyCircle.objects.get(invite_code=code, is_active=True)
            except FamilyCircle.DoesNotExist:
                form.add_error('invite_code', 'No family circle uses that invite code.')
            else:
                membership, created = FamilyMember.objects.get_or_create(
                    family_circle=circle,
                    user=request.user,
                    defaults={'role': 'MEMBER', 'joined_at': timezone.now()},
                )
                if not created:
                    membership.membership_status = 'ACTIVE'
                    membership.joined_at = timezone.now()
                    membership.save()
                messages.success(request, f'You joined "{circle.circle_name}"!')
                return redirect('circle_detail_id', circle_id=circle.id)
        messages.error(request, 'Please input correct invite code.')
    else:
        form = JoinCircleForm()
    return render(request, 'circles/circle_join.html', {'form': form})


@login_required
def leave_circle(request, circle_id=None):
    if circle_id:
        membership = get_object_or_404(
            FamilyMember,
            user=request.user,
            family_circle_id=circle_id,
            membership_status='ACTIVE',
        )
    else:
        membership = get_membership(request.user)

    if membership is None:
        return redirect('dashboard')
    if membership.role == 'ADMIN':
        messages.error(request, 'A circle must always have an administrator. Delete the circle instead.')
        return redirect('circle_detail_id', circle_id=membership.family_circle.id)

    if request.method == 'POST':
        name = membership.family_circle.circle_name
        membership.membership_status = 'REMOVED'
        membership.save()
        messages.success(request, f'You left "{name}".')
    return redirect('dashboard')


@login_required
def remove_member(request, member_id):
    target = get_object_or_404(
        FamilyMember,
        id=member_id,
        membership_status='ACTIVE',
    )
    membership = FamilyMember.objects.filter(
        user=request.user,
        family_circle=target.family_circle,
        membership_status='ACTIVE',
    ).first()

    if membership is None or membership.role != 'ADMIN':
        messages.error(request, 'Only the circle administrator can do that.')
        return redirect('dashboard')

    if request.method == 'POST':
        if target.user == request.user:
            messages.error(request, 'You cannot remove yourself. Delete the circle instead.')
        else:
            target.membership_status = 'REMOVED'
            target.save()
            messages.success(request, f'{target.user.first_name} was removed from the circle.')
    return redirect('circle_detail_id', circle_id=target.family_circle.id)
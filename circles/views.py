from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CircleForm, JoinCircleForm
from .models import FamilyCircle, FamilyMember
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
        messages.error(request, 'Circle name must be at least 3 characters.')
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
        return redirect('circle_join')
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


@login_required
def circle_join(request):
    if request.user.role != 'MEMBER':
        messages.error(request, 'Family Administrators create circles. Only Family Members join with a code.')
        return redirect('dashboard')
    if get_membership(request.user):
        messages.error(request, 'You already belong to a family circle.')
        return redirect('circle_detail')

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
                    # The user was removed earlier, so bring the membership back
                    membership.membership_status = 'ACTIVE'
                    membership.joined_at = timezone.now()
                    membership.save()
                messages.success(request, f'You joined "{circle.circle_name}"!')
                return redirect('circle_detail')
        messages.error(request, 'Please input correct invite code.')
    else:
        form = JoinCircleForm()
    return render(request, 'circles/circle_join.html', {'form': form})

@login_required
def leave_circle(request):
    membership = get_membership(request.user)
    if membership is None:
        return redirect('dashboard')
    if membership.role == 'ADMIN':
        messages.error(request, 'A circle must always have an administrator. Delete the circle instead.')
        return redirect('circle_detail')

    if request.method == 'POST':
        name = membership.family_circle.circle_name
        membership.membership_status = 'REMOVED'
        membership.save()
        messages.success(request, f'You left "{name}".')
    return redirect('dashboard')


@login_required
def remove_member(request, member_id):
    membership = get_membership(request.user)
    if membership is None or membership.role != 'ADMIN':
        messages.error(request, 'Only the circle administrator can do that.')
        return redirect('dashboard')

    # Only members of the administrator's own circle can be found here
    target = get_object_or_404(
        FamilyMember,
        id=member_id,
        family_circle=membership.family_circle,
        membership_status='ACTIVE',
    )
    if request.method == 'POST':
        if target.user == request.user:
            messages.error(request, 'You cannot remove yourself. Delete the circle instead.')
        else:
            target.membership_status = 'REMOVED'
            target.save()
            messages.success(request, f'{target.user.first_name} was removed from the circle.')
    return redirect('circle_detail')
from .models import FamilyMember


def get_membership(user):
    return (FamilyMember.objects
            .filter(user=user, membership_status='ACTIVE')
            .order_by('-joined_at')
            .first())


def get_all_memberships(user):
    return (FamilyMember.objects
            .filter(user=user, membership_status='ACTIVE')
            .select_related('family_circle', 'family_circle__created_by')
            .order_by('-joined_at'))


def circle_context(user):
    """Circle information that the dashboards show."""
    membership = get_membership(user)
    memberships = get_all_memberships(user)
    member_count = 0
    if membership:
        member_count = membership.family_circle.memberships.filter(membership_status='ACTIVE').count()
    return {
        'membership': membership,
        'memberships': memberships,
        'member_count': member_count,
    }
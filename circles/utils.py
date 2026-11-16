from .models import FamilyMember


def get_membership(user):
    """Returns the user's active membership, or None."""
    return (
        FamilyMember.objects
        .filter(user=user, membership_status='ACTIVE', family_circle__is_active=True)
        .select_related('family_circle')
        .first()
    )


def circle_context(user):
    """Circle information that the dashboards show."""
    membership = get_membership(user)
    member_count = 0
    if membership:
        member_count = membership.family_circle.memberships.filter(membership_status='ACTIVE').count()
    return {'membership': membership, 'member_count': member_count}
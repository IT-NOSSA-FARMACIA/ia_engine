from core.models import Team

def validate_team_user(user, team):
    if team in Team.objects.filter(user=user):
        return True
    else:
        return False

def get_user_team(user):
    return Team.objects.filter(user=user)
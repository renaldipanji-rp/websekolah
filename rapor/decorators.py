from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def is_guru(user):
    return user.groups.filter(name='Guru').exists()

def guru_required(view_func):
    decorated_view_func = user_passes_test(is_guru, login_url='/login/')(view_func)
    return decorated_view_func

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Admin').exists()
def is_WaliMurid(user):
    return user.is_authenticated and user.groups.filter(name='Wali Murid').exists()

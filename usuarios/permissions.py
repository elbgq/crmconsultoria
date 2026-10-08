
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def eh_socio(user):
    return hasattr(user, 'perfil') and user.perfil.cargo == 'socio'


def eh_consultor_senior_ou_socio(user):
    return hasattr(user, 'perfil') and user.perfil.cargo in ('socio', 'consultor_senior')


def cargo_minimo_senior_required(view):
    """Libera a view para superusuário, sócio e consultor sênior; os demais recebem 403."""
    @wraps(view)
    @login_required
    def _view(request, *args, **kwargs):
        if request.user.is_superuser or eh_consultor_senior_ou_socio(request.user):
            return view(request, *args, **kwargs)
        raise PermissionDenied
    return _view

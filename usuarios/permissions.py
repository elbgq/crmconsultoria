
def eh_socio(user):
    return hasattr(user, 'perfil') and user.perfil.cargo == 'socio'


def eh_consultor_senior_ou_socio(user):
    return hasattr(user, 'perfil') and user.perfil.cargo in ('socio', 'consultor_senior')
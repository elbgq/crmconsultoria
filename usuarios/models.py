from django.db import models
from django.conf import settings
from crm_core.models import ModeloBase, AreaConsultoria


class Cargo(models.TextChoices):
    SOCIO = 'socio', 'Sócio'
    CONSULTOR_SENIOR = 'consultor_senior', 'Consultor Sênior'
    CONSULTOR = 'consultor', 'Consultor'
    ADMINISTRATIVO = 'administrativo', 'Administrativo'


class Perfil(ModeloBase):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil'
    )
    cargo = models.CharField(max_length=20, choices=Cargo.choices, default=Cargo.CONSULTOR)
    area_principal = models.CharField(max_length=20, choices=AreaConsultoria.choices, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='perfis/', null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta(ModeloBase.Meta):
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        ordering = ['usuario__first_name']

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.get_cargo_display()})" # type: ignore
    
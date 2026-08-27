from django.conf import settings
from django.db import models


class LogAuditoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="logs_auditoria",
    )
    acao = models.CharField(max_length=100)
    modulo = models.CharField(max_length=100)
    objeto = models.CharField(max_length=255, blank=True)
    dados_anteriores = models.JSONField(null=True, blank=True)
    dados_novos = models.JSONField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"[{self.criado_em}] {self.usuario} - {self.acao} ({self.modulo})"

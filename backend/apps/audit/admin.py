from django.contrib import admin

from .models import LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "usuario", "acao", "modulo", "objeto", "ip")
    list_filter = ("modulo", "acao")
    search_fields = ("objeto", "usuario__username")
    readonly_fields = [f.name for f in LogAuditoria._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

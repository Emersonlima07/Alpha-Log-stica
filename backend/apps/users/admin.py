from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "perfil", "empresa", "filial", "is_staff", "ativo")
    list_filter = ("perfil", "empresa", "is_staff", "ativo")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Dados do ERP", {"fields": ("perfil", "empresa", "filial", "telefone", "ativo")}),
    )

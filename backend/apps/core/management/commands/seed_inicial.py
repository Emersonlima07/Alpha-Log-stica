from django.core.management.base import BaseCommand

from apps.core.models import Empresa, Filial
from apps.users.models import Perfil, User


class Command(BaseCommand):
    help = "Cria empresa, filial e usuario administrador iniciais para comecar a usar o sistema."

    def handle(self, *args, **options):
        empresa, criada = Empresa.objects.get_or_create(
            cnpj="00.000.000/0001-00",
            defaults={"razao_social": "Alpha Logística Ltda", "nome_fantasia": "Alpha Logística"},
        )
        if criada:
            self.stdout.write(self.style.SUCCESS(f"Empresa criada: {empresa}"))

        filial, _ = Filial.objects.get_or_create(
            empresa=empresa,
            codigo="MATRIZ",
            defaults={"nome": "Matriz", "endereco": "Endereco de exemplo, 123"},
        )

        if not User.objects.filter(username="Emersonlima07").exists():
            admin = User.objects.create_superuser(
                username="Emersonlima07",
                email="admin@erp.local",
                password="El031620**",
            )
            admin.perfil = Perfil.ADMINISTRADOR
            admin.empresa = empresa
            admin.filial = filial
            admin.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Usuario administrador criado -> login: Emersonlima07 / senha: El031620** "
                    "(troque a senha imediatamente)"
                )
            )
        else:
            self.stdout.write("Usuario ja existe, nada a fazer.")

from .models import Empresa, Filial


class EmpresaRepository:
    """Unico ponto de acesso ao ORM para o modelo Empresa."""

    model = Empresa

    def listar(self):
        return self.model.objects.all()

    def obter_por_id(self, empresa_id):
        return self.model.objects.filter(id=empresa_id).first()

    def obter_por_cnpj(self, cnpj):
        return self.model.objects.filter(cnpj=cnpj).first()

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def atualizar(self, empresa, **dados):
        for campo, valor in dados.items():
            setattr(empresa, campo, valor)
        empresa.save()
        return empresa


class FilialRepository:
    model = Filial

    def listar_por_empresa(self, empresa_id):
        return self.model.objects.filter(empresa_id=empresa_id)

    def obter_por_id(self, filial_id):
        return self.model.objects.filter(id=filial_id).first()

    def criar(self, **dados):
        return self.model.objects.create(**dados)

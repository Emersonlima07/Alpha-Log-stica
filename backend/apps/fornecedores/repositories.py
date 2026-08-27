from .models import Fornecedor


class FornecedorRepository:
    model = Fornecedor

    def listar(self):
        return self.model.objects.all()

    def obter_por_id(self, fornecedor_id):
        return self.model.objects.filter(id=fornecedor_id).first()

    def obter_por_cnpj(self, cnpj):
        return self.model.objects.filter(cnpj=cnpj).first()

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def atualizar(self, fornecedor, **dados):
        for campo, valor in dados.items():
            setattr(fornecedor, campo, valor)
        fornecedor.save()
        return fornecedor

from .models import Categoria, Fabricante, Produto


class ProdutoRepository:
    model = Produto

    def listar(self):
        return self.model.objects.select_related("categoria", "fabricante", "fornecedor_principal").all()

    def obter_por_id(self, produto_id):
        return self.model.objects.filter(id=produto_id).first()

    def obter_por_codigo_interno(self, codigo_interno):
        return self.model.objects.filter(codigo_interno=codigo_interno).first()

    def obter_por_codigo_barras(self, codigo_barras):
        return self.model.objects.filter(codigo_barras=codigo_barras).first()

    def criar(self, **dados):
        produto = self.model(**dados)
        produto.full_clean()
        produto.save()
        return produto

    def atualizar(self, produto, **dados):
        for campo, valor in dados.items():
            setattr(produto, campo, valor)
        produto.full_clean()
        produto.save()
        return produto


class CategoriaRepository:
    model = Categoria

    def listar(self):
        return self.model.objects.all()

    def criar(self, **dados):
        return self.model.objects.create(**dados)


class FabricanteRepository:
    model = Fabricante

    def listar(self):
        return self.model.objects.all()

    def criar(self, **dados):
        return self.model.objects.create(**dados)

from .models import Cotacao, PedidoCompra, PedidoCompraItem, SolicitacaoCompra


class SolicitacaoCompraRepository:
    model = SolicitacaoCompra

    def listar(self):
        return self.model.objects.select_related("produto", "filial", "solicitante").all()

    def obter_por_id(self, solicitacao_id):
        return self.model.objects.filter(id=solicitacao_id).first()

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def atualizar(self, solicitacao, **dados):
        for campo, valor in dados.items():
            setattr(solicitacao, campo, valor)
        solicitacao.save()
        return solicitacao


class CotacaoRepository:
    model = Cotacao

    def listar_por_solicitacao(self, solicitacao_id):
        return self.model.objects.filter(solicitacao_id=solicitacao_id).select_related("fornecedor")

    def obter_por_id(self, cotacao_id):
        return self.model.objects.filter(id=cotacao_id).first()

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def desmarcar_selecionadas(self, solicitacao_id):
        self.model.objects.filter(solicitacao_id=solicitacao_id).update(selecionada=False)


class PedidoCompraRepository:
    model = PedidoCompra

    def listar(self):
        return self.model.objects.select_related("fornecedor", "filial").all()

    def obter_por_id(self, pedido_id):
        return self.model.objects.filter(id=pedido_id).first()

    def proximo_numero(self):
        ultimo = self.model.todos_objects.order_by("-id").first()
        proximo = (ultimo.id + 1) if ultimo else 1
        return f"PC-{proximo:06d}"

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def atualizar(self, pedido, **dados):
        for campo, valor in dados.items():
            setattr(pedido, campo, valor)
        pedido.save()
        return pedido


class PedidoCompraItemRepository:
    model = PedidoCompraItem

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def listar_por_pedido(self, pedido_id):
        return self.model.objects.filter(pedido_id=pedido_id).select_related("produto")

    def salvar(self, item):
        item.save()
        return item

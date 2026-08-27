from .models import Recebimento, RecebimentoItem


class RecebimentoRepository:
    model = Recebimento

    def listar(self):
        return self.model.objects.select_related("pedido_compra", "responsavel").all()

    def obter_por_id(self, recebimento_id):
        return self.model.objects.filter(id=recebimento_id).first()

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def atualizar(self, recebimento, **dados):
        for campo, valor in dados.items():
            setattr(recebimento, campo, valor)
        recebimento.save()
        return recebimento


class RecebimentoItemRepository:
    model = RecebimentoItem

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def listar_por_recebimento(self, recebimento_id):
        return self.model.objects.filter(recebimento_id=recebimento_id).select_related("produto", "pedido_item")

    def obter_por_id(self, item_id):
        return self.model.objects.filter(id=item_id).first()

    def salvar(self, item):
        item.save()
        return item

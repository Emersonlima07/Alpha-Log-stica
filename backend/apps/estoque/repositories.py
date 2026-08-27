from django.db.models import Q

from .models import Lote, MovimentoEstoque


class LoteRepository:
    model = Lote

    def obter_ou_criar(self, *, produto, filial, numero_lote, data_validade=None, valor_unitario=0):
        lote, _criado = self.model.objects.get_or_create(
            produto=produto,
            filial=filial,
            numero_lote=numero_lote or "UNICO",
            defaults={
                "data_validade": data_validade,
                "quantidade_atual": 0,
                "valor_unitario": valor_unitario or 0,
            },
        )
        return lote

    def obter(self, *, produto, filial, numero_lote):
        return self.model.objects.filter(
            produto=produto, filial=filial, numero_lote=numero_lote or "UNICO"
        ).first()

    def por_produto(self, produto_id):
        return self.model.objects.filter(produto_id=produto_id, quantidade_atual__gt=0)

    def por_validade_ate(self, data_limite):
        return self.model.objects.filter(
            data_validade__isnull=False, data_validade__lte=data_limite, quantidade_atual__gt=0
        )

    def salvar(self, lote):
        lote.full_clean()
        lote.save()
        return lote


class MovimentoEstoqueRepository:
    model = MovimentoEstoque

    def criar(self, **dados):
        return self.model.objects.create(**dados)

    def historico(self, *, produto_id=None, filial_id=None, tipo=None):
        qs = self.model.objects.select_related("produto", "lote", "filial_origem", "filial_destino", "usuario")
        if produto_id:
            qs = qs.filter(produto_id=produto_id)
        if filial_id:
            qs = qs.filter(Q(filial_origem_id=filial_id) | Q(filial_destino_id=filial_id))
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs.distinct()

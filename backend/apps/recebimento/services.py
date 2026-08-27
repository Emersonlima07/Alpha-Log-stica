from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import AuditoriaService
from apps.compras.models import StatusPedido
from apps.estoque.services import EstoqueService
from apps.produtos.models import Produto

from .models import StatusRecebimento
from .parsers import XmlNfeInvalidoError, parsear_xml_nfe
from .repositories import RecebimentoItemRepository, RecebimentoRepository


class RecebimentoService:
    def __init__(
        self,
        recebimento_repository: RecebimentoRepository = None,
        item_repository: RecebimentoItemRepository = None,
        estoque_service: EstoqueService = None,
        auditoria: AuditoriaService = None,
    ):
        self.recebimentos = recebimento_repository or RecebimentoRepository()
        self.itens = item_repository or RecebimentoItemRepository()
        self.estoque = estoque_service or EstoqueService()
        self.auditoria = auditoria or AuditoriaService()

    def listar(self):
        return self.recebimentos.listar()

    # ------------------------------------------------------------------
    # Abertura do recebimento (manual, a partir do pedido)
    # ------------------------------------------------------------------
    def iniciar_recebimento(self, *, pedido_compra, responsavel, numero_nf="", chave_nfe=""):
        if pedido_compra.status in (StatusPedido.RECEBIDO, StatusPedido.CANCELADO):
            raise ValidationError("Este pedido ja foi totalmente recebido ou esta cancelado.")

        recebimento = self.recebimentos.criar(
            pedido_compra=pedido_compra, numero_nf=numero_nf, chave_nfe=chave_nfe, responsavel=responsavel,
        )
        for pedido_item in pedido_compra.itens.all():
            pendente = pedido_item.quantidade_pendente
            if pendente <= 0:
                continue
            self.itens.criar(
                recebimento=recebimento, pedido_item=pedido_item, produto=pedido_item.produto,
                quantidade_nf=pendente, quantidade_conferida=0, valor_unitario=pedido_item.valor_unitario,
            )
        self.auditoria.registrar(usuario=responsavel, acao="INICIAR_RECEBIMENTO", modulo="Recebimento", objeto=str(recebimento))
        return recebimento

    # ------------------------------------------------------------------
    # Abertura via importacao de XML da NF-e
    # ------------------------------------------------------------------
    def importar_xml_nfe(self, *, pedido_compra, xml_content, responsavel):
        try:
            dados = parsear_xml_nfe(xml_content)
        except XmlNfeInvalidoError as exc:
            raise ValidationError(str(exc))

        recebimento = self.recebimentos.criar(
            pedido_compra=pedido_compra, numero_nf=dados["numero_nf"], chave_nfe=dados["chave_nfe"],
            responsavel=responsavel,
            observacoes=f"Importado via XML. Emitente: {dados['nome_emitente']} ({dados['cnpj_emitente']})",
        )

        itens_sem_correspondencia = []
        for item in dados["itens"]:
            produto = (
                Produto.objects.filter(codigo_interno=item["codigo_produto"]).first()
                or Produto.objects.filter(codigo_barras=item["codigo_barras"]).first()
            )
            if not produto:
                itens_sem_correspondencia.append(item["descricao"] or item["codigo_produto"])
                continue
            pedido_item = pedido_compra.itens.filter(produto=produto).first()
            self.itens.criar(
                recebimento=recebimento, pedido_item=pedido_item, produto=produto,
                quantidade_nf=item["quantidade"], quantidade_conferida=0, valor_unitario=item["valor_unitario"],
            )

        if itens_sem_correspondencia:
            recebimento.observacoes += (
                f" | Itens do XML sem produto cadastrado (nao importados, "
                f"precisam ser lancados manualmente): {', '.join(itens_sem_correspondencia)}"
            )
            recebimento.save(update_fields=["observacoes"])

        self.auditoria.registrar(
            usuario=responsavel, acao="IMPORTAR_XML_NFE", modulo="Recebimento", objeto=str(recebimento),
            dados_novos={"itens_sem_correspondencia": itens_sem_correspondencia},
        )
        return recebimento

    # ------------------------------------------------------------------
    # Conferencia fisica (por lote, validade e quantidade)
    # ------------------------------------------------------------------
    def conferir_item(self, *, item, quantidade_conferida, usuario, numero_lote="", data_validade=None):
        if item.recebimento.status != StatusRecebimento.EM_CONFERENCIA:
            raise ValidationError("Este recebimento ja foi finalizado; nao e mais possivel alterar a conferencia.")

        item.quantidade_conferida = quantidade_conferida
        if numero_lote:
            item.numero_lote = numero_lote
        if data_validade:
            item.data_validade = data_validade
        self.itens.salvar(item)

        self.auditoria.registrar(
            usuario=usuario, acao="CONFERIR_ITEM_RECEBIMENTO", modulo="Recebimento", objeto=str(item),
            dados_novos={"quantidade_conferida": str(quantidade_conferida), "divergencia": item.tem_divergencia},
        )
        return item

    # ------------------------------------------------------------------
    # Aprovacao -> entrada automatica no estoque (integra com Modulo 3)
    # ------------------------------------------------------------------
    @transaction.atomic
    def aprovar_recebimento(self, *, recebimento, aprovador):
        if recebimento.status != StatusRecebimento.EM_CONFERENCIA:
            raise ValidationError("Este recebimento ja foi processado (aprovado ou rejeitado).")

        itens = list(recebimento.itens.all())
        if not itens:
            raise ValidationError("Este recebimento nao tem itens conferidos.")

        for item in itens:
            if item.quantidade_conferida <= 0:
                continue
            self.estoque.registrar_entrada(
                produto=item.produto,
                filial=recebimento.pedido_compra.filial,
                quantidade=item.quantidade_conferida,
                usuario=aprovador,
                numero_lote=item.numero_lote or None,
                data_validade=item.data_validade,
                valor_unitario=item.valor_unitario,
                motivo=f"Recebimento NF {recebimento.numero_nf or recebimento.id} (Pedido {recebimento.pedido_compra.numero})",
            )
            if item.pedido_item:
                item.pedido_item.quantidade_recebida += item.quantidade_conferida
                item.pedido_item.save(update_fields=["quantidade_recebida"])

        self._atualizar_status_pedido(recebimento.pedido_compra)
        self.recebimentos.atualizar(recebimento, status=StatusRecebimento.APROVADO)

        self.auditoria.registrar(
            usuario=aprovador, acao="APROVAR_RECEBIMENTO", modulo="Recebimento", objeto=str(recebimento),
            dados_novos={"tinha_divergencia": recebimento.tem_divergencia},
        )
        return recebimento

    def rejeitar_recebimento(self, *, recebimento, aprovador, motivo):
        if not motivo:
            raise ValidationError("Informe o motivo da rejeicao do recebimento.")
        if recebimento.status != StatusRecebimento.EM_CONFERENCIA:
            raise ValidationError("Este recebimento ja foi processado.")

        self.recebimentos.atualizar(recebimento, status=StatusRecebimento.REJEITADO, observacoes=motivo)
        self.auditoria.registrar(usuario=aprovador, acao="REJEITAR_RECEBIMENTO", modulo="Recebimento", objeto=str(recebimento))
        return recebimento

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _atualizar_status_pedido(self, pedido):
        itens = list(pedido.itens.all())
        if not itens:
            return
        if all(item.quantidade_recebida >= item.quantidade for item in itens):
            pedido.status = StatusPedido.RECEBIDO
        elif any(item.quantidade_recebida > 0 for item in itens):
            pedido.status = StatusPedido.PARCIALMENTE_RECEBIDO
        else:
            return
        pedido.save(update_fields=["status"])

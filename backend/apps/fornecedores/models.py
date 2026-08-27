from django.db import models

from apps.core.models import BaseModel


class Fornecedor(BaseModel):
    """
    Cadastro de fornecedores (Modulo 4). Usado tanto pelo cadastro de
    produtos (fornecedor principal) quanto pelo fluxo de compras
    (cotacoes e pedidos).

    Os campos de avaliacao comecam simples aqui; o Modulo 13 (CRM de
    Fornecedores) vai aprofundar isso com historico de pontualidade e
    qualidade calculado a partir dos recebimentos de verdade.
    """

    razao_social = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255, blank=True)
    cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    contato_nome = models.CharField(max_length=150, blank=True)
    prazo_pagamento_padrao_dias = models.PositiveIntegerField(default=30)

    avaliacao_pontualidade = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    avaliacao_qualidade = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["razao_social"]

    def __str__(self):
        return self.nome_fantasia or self.razao_social

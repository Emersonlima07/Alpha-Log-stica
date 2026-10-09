"""Controle simples de estoque e vendas (terminal).

Uso:
    python estoque_vendas.py

Os dados ficam salvos em `estoque_vendas.json`, na mesma pasta do script.
Não precisa instalar nada: usa apenas a biblioteca padrão do Python 3.
"""

import json
from datetime import datetime
from pathlib import Path

ARQUIVO_DADOS = Path(__file__).with_name("estoque_vendas.json")


# ----------------------------------------------------------------------
# Persistência
# ----------------------------------------------------------------------
def carregar_dados():
    if ARQUIVO_DADOS.exists():
        with open(ARQUIVO_DADOS, encoding="utf-8") as f:
            return json.load(f)
    return {"produtos": {}, "vendas": []}


def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------
# Entrada de dados
# ----------------------------------------------------------------------
def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("  Valor não pode ficar vazio.")


def ler_numero(mensagem, inteiro=False, minimo=0):
    while True:
        bruto = input(mensagem).strip().replace(",", ".")
        try:
            valor = int(bruto) if inteiro else float(bruto)
        except ValueError:
            print("  Digite um número válido.")
            continue
        if valor < minimo:
            print(f"  O valor deve ser no mínimo {minimo}.")
            continue
        return valor


def moeda(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def escolher_produto(dados):
    if not dados["produtos"]:
        print("\nNenhum produto cadastrado.")
        return None
    listar_estoque(dados, resumo=False)
    codigo = ler_texto("Código do produto: ").upper()
    if codigo not in dados["produtos"]:
        print("  Produto não encontrado.")
        return None
    return codigo


# ----------------------------------------------------------------------
# Operações
# ----------------------------------------------------------------------
def cadastrar_produto(dados):
    print("\n--- Cadastrar produto ---")
    codigo = ler_texto("Código: ").upper()
    if codigo in dados["produtos"]:
        print("  Já existe um produto com esse código.")
        return
    dados["produtos"][codigo] = {
        "nome": ler_texto("Nome: "),
        "custo": ler_numero("Preço de custo (R$): "),
        "preco": ler_numero("Preço de venda (R$): "),
        "quantidade": ler_numero("Quantidade inicial: ", inteiro=True),
        "minimo": ler_numero("Estoque mínimo (alerta): ", inteiro=True),
    }
    salvar_dados(dados)
    print("  Produto cadastrado!")


def entrada_estoque(dados):
    print("\n--- Entrada de estoque ---")
    codigo = escolher_produto(dados)
    if not codigo:
        return
    qtd = ler_numero("Quantidade que entrou: ", inteiro=True, minimo=1)
    dados["produtos"][codigo]["quantidade"] += qtd
    salvar_dados(dados)
    print(f"  Novo saldo: {dados['produtos'][codigo]['quantidade']}")


def registrar_venda(dados):
    print("\n--- Registrar venda ---")
    codigo = escolher_produto(dados)
    if not codigo:
        return
    produto = dados["produtos"][codigo]
    qtd = ler_numero("Quantidade vendida: ", inteiro=True, minimo=1)
    if qtd > produto["quantidade"]:
        print(f"  Estoque insuficiente (disponível: {produto['quantidade']}).")
        return

    preco = produto["preco"]
    resposta = input(f"Preço unitário [{moeda(preco)}] (Enter mantém): ").strip()
    if resposta:
        try:
            preco = float(resposta.replace(",", "."))
        except ValueError:
            print("  Preço inválido, usando o preço cadastrado.")

    produto["quantidade"] -= qtd
    venda = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "codigo": codigo,
        "nome": produto["nome"],
        "quantidade": qtd,
        "preco_unitario": preco,
        "custo_unitario": produto["custo"],
        "total": round(qtd * preco, 2),
    }
    dados["vendas"].append(venda)
    salvar_dados(dados)
    print(f"  Venda registrada: {moeda(venda['total'])}. "
          f"Saldo restante: {produto['quantidade']}")
    if produto["quantidade"] <= produto["minimo"]:
        print("  ATENÇÃO: produto atingiu o estoque mínimo!")


def listar_estoque(dados, resumo=True):
    print(f"\n{'CÓDIGO':<10}{'PRODUTO':<25}{'QTD':>6}{'CUSTO':>14}{'VENDA':>14}")
    print("-" * 69)
    valor_custo = valor_venda = 0
    for codigo, p in sorted(dados["produtos"].items()):
        alerta = " !" if p["quantidade"] <= p["minimo"] else ""
        print(f"{codigo:<10}{p['nome'][:24]:<25}{p['quantidade']:>6}"
              f"{moeda(p['custo']):>14}{moeda(p['preco']):>14}{alerta}")
        valor_custo += p["quantidade"] * p["custo"]
        valor_venda += p["quantidade"] * p["preco"]
    if resumo:
        print("-" * 69)
        print(f"Itens em estoque:            {sum(p['quantidade'] for p in dados['produtos'].values())}")
        print(f"Valor do estoque (custo):    {moeda(valor_custo)}")
        print(f"Valor do estoque (venda):    {moeda(valor_venda)}")
        print(f"Lucro potencial:             {moeda(valor_venda - valor_custo)}")
        print("( ! = abaixo ou no estoque mínimo )")


def relatorio_vendas(dados):
    print("\n--- Relatório de vendas ---")
    if not dados["vendas"]:
        print("Nenhuma venda registrada.")
        return

    filtro = input("Filtrar por mês (AAAA-MM) ou Enter para tudo: ").strip()
    vendas = [v for v in dados["vendas"] if v["data"].startswith(filtro)]
    if not vendas:
        print("Nenhuma venda nesse período.")
        return

    por_produto = {}
    for v in vendas:
        item = por_produto.setdefault(
            v["codigo"], {"nome": v["nome"], "qtd": 0, "total": 0.0, "lucro": 0.0})
        item["qtd"] += v["quantidade"]
        item["total"] += v["total"]
        item["lucro"] += v["total"] - v["quantidade"] * v["custo_unitario"]

    print(f"\n{'PRODUTO':<25}{'QTD':>6}{'FATURADO':>16}{'LUCRO':>16}")
    print("-" * 63)
    ranking = sorted(por_produto.values(), key=lambda i: i["total"], reverse=True)
    for item in ranking:
        print(f"{item['nome'][:24]:<25}{item['qtd']:>6}"
              f"{moeda(item['total']):>16}{moeda(item['lucro']):>16}")

    faturamento = sum(i["total"] for i in ranking)
    lucro = sum(i["lucro"] for i in ranking)
    print("-" * 63)
    print(f"Número de vendas:   {len(vendas)}")
    print(f"Faturamento total:  {moeda(faturamento)}")
    print(f"Lucro bruto:        {moeda(lucro)}")
    print(f"Ticket médio:       {moeda(faturamento / len(vendas))}")
    if faturamento:
        print(f"Margem:             {lucro / faturamento * 100:.1f}%")


def historico_vendas(dados):
    print("\n--- Histórico de vendas ---")
    if not dados["vendas"]:
        print("Nenhuma venda registrada.")
        return
    for v in dados["vendas"][-30:]:
        print(f"{v['data']}  {v['nome'][:24]:<25}{v['quantidade']:>4} x "
              f"{moeda(v['preco_unitario']):>12} = {moeda(v['total']):>14}")


# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------
def main():
    dados = carregar_dados()
    opcoes = {
        "1": ("Cadastrar produto", cadastrar_produto),
        "2": ("Entrada de estoque", entrada_estoque),
        "3": ("Registrar venda", registrar_venda),
        "4": ("Ver estoque", listar_estoque),
        "5": ("Relatório de vendas", relatorio_vendas),
        "6": ("Histórico de vendas (últimas 30)", historico_vendas),
    }
    while True:
        print("\n===== CONTROLE DE ESTOQUE E VENDAS =====")
        for chave, (descricao, _) in opcoes.items():
            print(f"{chave} - {descricao}")
        print("0 - Sair")
        escolha = input("Opção: ").strip()
        if escolha == "0":
            print("Até logo!")
            break
        if escolha in opcoes:
            opcoes[escolha][1](dados)
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()

"""
Leitor basico de XML de NF-e (Modulo 5: "Importacao XML da NF-e").

IMPORTANTE: isto le e interpreta um arquivo XML de NF-e que voce ja tem
em maos (por exemplo, recebido do fornecedor). Nao e uma integracao
oficial com a SEFAZ -- emitir, validar ou consultar notas fiscais junto
ao governo exige certificado digital A1/A3 e um webservice proprio
(isso e escopo do Modulo 12 - Faturamento, ainda nao implementado).
Aqui, o objetivo e so evitar redigitar os itens na mao quando o XML
existe.
"""

from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree as ET


class XmlNfeInvalidoError(Exception):
    pass


def _nome_local(tag: str) -> str:
    """Remove o namespace da tag (ex: '{http://...}infNFe' -> 'infNFe')."""
    return tag.split("}")[-1] if "}" in tag else tag


def _primeiro(elemento, nome_tag):
    if elemento is None:
        return None
    for filho in elemento.iter():
        if _nome_local(filho.tag) == nome_tag:
            return filho
    return None


def _texto(elemento, nome_tag, padrao=""):
    achado = _primeiro(elemento, nome_tag)
    return achado.text if achado is not None and achado.text else padrao


def _decimal(valor, padrao="0"):
    try:
        return Decimal(valor or padrao)
    except InvalidOperation:
        return Decimal(padrao)


def parsear_xml_nfe(xml_content: str) -> dict:
    """
    Recebe o conteudo (string) de um XML de NF-e e devolve um dict com:
    numero_nf, chave_nfe, cnpj_emitente, nome_emitente e uma lista de
    itens (codigo_produto, descricao, quantidade, valor_unitario).

    Levanta XmlNfeInvalidoError com uma mensagem clara se o arquivo nao
    for um XML valido ou nao tiver a estrutura minima de uma NF-e.
    """
    try:
        raiz = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        raise XmlNfeInvalidoError(f"O arquivo nao e um XML valido: {exc}")

    inf_nfe = _primeiro(raiz, "infNFe")
    if inf_nfe is None:
        raise XmlNfeInvalidoError(
            "Este arquivo nao parece ser uma NF-e (a tag <infNFe> nao foi encontrada)."
        )

    ide = _primeiro(inf_nfe, "ide")
    numero_nf = _texto(ide, "nNF")

    chave_nfe = ""
    id_attr = inf_nfe.get("Id", "")
    if id_attr.startswith("NFe"):
        chave_nfe = id_attr[3:]

    emit = _primeiro(inf_nfe, "emit")
    cnpj_emitente = _texto(emit, "CNPJ")
    nome_emitente = _texto(emit, "xNome")

    itens = []
    for det in [e for e in inf_nfe.iter() if _nome_local(e.tag) == "det"]:
        prod = _primeiro(det, "prod")
        if prod is None:
            continue
        itens.append({
            "codigo_produto": _texto(prod, "cProd"),
            "codigo_barras": _texto(prod, "cEAN"),
            "descricao": _texto(prod, "xProd"),
            "quantidade": _decimal(_texto(prod, "qCom")),
            "valor_unitario": _decimal(_texto(prod, "vUnCom")),
        })

    if not itens:
        raise XmlNfeInvalidoError("Nenhum item de produto (tag <det>/<prod>) foi encontrado no XML.")

    return {
        "numero_nf": numero_nf,
        "chave_nfe": chave_nfe,
        "cnpj_emitente": cnpj_emitente,
        "nome_emitente": nome_emitente,
        "itens": itens,
    }

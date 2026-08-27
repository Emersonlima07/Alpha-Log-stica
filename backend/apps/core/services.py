from django.core.exceptions import ValidationError

from .repositories import EmpresaRepository, FilialRepository


class EmpresaService:
    def __init__(self, repository: EmpresaRepository = None):
        self.repository = repository or EmpresaRepository()

    def listar(self):
        return self.repository.listar()

    def criar_empresa(self, *, razao_social, cnpj, nome_fantasia=""):
        if self.repository.obter_por_cnpj(cnpj):
            raise ValidationError("Ja existe uma empresa cadastrada com este CNPJ.")
        return self.repository.criar(
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            cnpj=cnpj,
        )


class FilialService:
    def __init__(self, repository: FilialRepository = None):
        self.repository = repository or FilialRepository()

    def listar_por_empresa(self, empresa_id):
        return self.repository.listar_por_empresa(empresa_id)

    def criar_filial(self, *, empresa_id, codigo, nome, endereco=""):
        return self.repository.criar(
            empresa_id=empresa_id, codigo=codigo, nome=nome, endereco=endereco
        )

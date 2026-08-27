from .models import User


class UserRepository:
    model = User

    def listar_por_empresa(self, empresa_id):
        return self.model.objects.filter(empresa_id=empresa_id)

    def obter_por_id(self, user_id):
        return self.model.objects.filter(id=user_id).first()

    def obter_por_username(self, username):
        return self.model.objects.filter(username=username).first()

    def criar(self, *, password, **dados):
        user = self.model(**dados)
        user.set_password(password)
        user.save()
        return user

    def atualizar(self, user, **dados):
        for campo, valor in dados.items():
            setattr(user, campo, valor)
        user.save()
        return user

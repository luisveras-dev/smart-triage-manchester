from datetime import datetime
from typing import Optional


class Paciente:
    """
    Classe Base de Paciente (Pilar de POO: Encapsulamento).
    Protege os dados sensíveis através de atributos privados e propriedades.
    """
    def __init__(
        self,
        nome: str,
        cpf: str,
        idade: int,
        paciente_id: Optional[int] = None,
        criado_em: Optional[datetime] = None
    ):
        self._id = paciente_id
        self._nome = nome.strip()
        self._cpf = "".join(filter(str.isalnum, cpf))
        self._idade = int(idade)
        self._eh_preferencial = False
        self._criado_em = criado_em or datetime.now()

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: int):
        self._id = valor

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("O nome do paciente não pode ser vazio.")
        self._nome = valor.strip()

    @property
    def cpf(self) -> str:
        return self._cpf

    @property
    def idade(self) -> int:
        return self._idade

    @idade.setter
    def idade(self, valor: int):
        if valor < 0 or valor > 130:
            raise ValueError("Idade inválida.")
        self._idade = valor

    @property
    def eh_preferencial(self) -> bool:
        return self._eh_preferencial

    @property
    def criado_em(self) -> datetime:
        return self._criado_em

    def peso_prioridade_desempate(self) -> int:
        """
        Método Polimórfico (Polimorfismo em tempo de execução).
        Pacientes comuns possuem peso padrão de desempate = 1 (menor preferência).
        """
        return 1

    def tipo_atendimento(self) -> str:
        return "Geral"

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "nome": self._nome,
            "cpf": self._cpf,
            "idade": self._idade,
            "eh_preferencial": self.eh_preferencial,
            "tipo_atendimento": self.tipo_atendimento(),
            "peso_desempate": self.peso_prioridade_desempate()
        }


class PacientePreferencial(Paciente):
    """
    Subclasse para Atendimento Preferencial (Pilar de POO: Herança).
    Aplica-se por lei a idosos (idade >= 60), gestantes, lactantes,
    pessoas com deficiência ou comorbidades prioritárias.
    """
    def __init__(
        self,
        nome: str,
        cpf: str,
        idade: int,
        motivo_preferencia: str = "Lei nº 10.048/2000",
        paciente_id: Optional[int] = None,
        criado_em: Optional[datetime] = None
    ):
        super().__init__(nome, cpf, idade, paciente_id, criado_em)
        self._eh_preferencial = True
        self._motivo_preferencia = motivo_preferencia

    @property
    def motivo_preferencia(self) -> str:
        return self._motivo_preferencia

    def peso_prioridade_desempate(self) -> int:
        """
        Sobrescrita Polimórfica (Polimorfismo).
        Pacientes preferenciais têm peso 0 no desempate de mesma cor de Manchester,
        sendo chamados antes dos pacientes comuns do mesmo nível de gravidade.
        """
        return 0

    def tipo_atendimento(self) -> str:
        return f"Preferencial ({self._motivo_preferencia})"

    def to_dict(self) -> dict:
        dados = super().to_dict()
        dados["motivo_preferencia"] = self._motivo_preferencia
        return dados

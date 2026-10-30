from enum import Enum
from datetime import datetime
from typing import Optional


class GrauRisco(Enum):
    """
    Protocolo de Manchester:
    Score 1 = Vermelho (Emergência - 0 min)
    Score 2 = Laranja (Muito Urgente - 10 min)
    Score 3 = Amarelo (Urgente - 60 min)
    Score 4 = Verde (Pouco Urgente - 120 min)
    Score 5 = Azul (Não Urgente - 240 min)
    """
    VERMELHO = (1, "Vermelho", 0, "Emergência - Atendimento imediato")
    LARANJA = (2, "Laranja", 10, "Muito Urgente - Até 10 minutos")
    AMARELO = (3, "Amarelo", 60, "Urgente - Até 60 minutos")
    VERDE = (4, "Verde", 120, "Pouco Urgente - Até 120 minutos")
    AZUL = (5, "Azul", 240, "Não Urgente - Até 240 minutos")

    def __init__(self, score: int, cor: str, tempo_espera_min: int, descricao: str):
        self.score = score
        self.cor = cor
        self.tempo_espera_min = tempo_espera_min
        self.descricao = descricao

    @classmethod
    def por_score(cls, score: int) -> "GrauRisco":
        for item in cls:
            if item.score == score:
                return item
        return cls.AZUL

    @classmethod
    def por_nome(cls, nome: str) -> "GrauRisco":
        nome_limpo = (nome or "").strip().upper()
        for item in cls:
            if item.name == nome_limpo or item.cor.upper() == nome_limpo:
                return item
        return cls.AZUL


class Triagem:
    """
    Encapsula os dados da triagem médica de um paciente.
    Aplica encapsulamento estrito com atributos protegidos.
    """
    def __init__(
        self,
        sintomas: str,
        grau_risco: GrauRisco,
        justificativa_ia: str = "",
        triagem_id: Optional[int] = None,
        paciente_id: Optional[int] = None,
        criado_em: Optional[datetime] = None
    ):
        self._id = triagem_id
        self._paciente_id = paciente_id
        self._sintomas = sintomas.strip()
        self._grau_risco = grau_risco
        self._justificativa_ia = justificativa_ia
        self._status = "AGUARDANDO"
        self._criado_em = criado_em or datetime.now()

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: int):
        self._id = valor

    @property
    def paciente_id(self) -> Optional[int]:
        return self._paciente_id

    @paciente_id.setter
    def paciente_id(self, valor: int):
        self._paciente_id = valor

    @property
    def sintomas(self) -> str:
        return self._sintomas

    @property
    def grau_risco(self) -> GrauRisco:
        return self._grau_risco

    @property
    def justificativa_ia(self) -> str:
        return self._justificativa_ia

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, novo_status: str):
        self._status = novo_status.upper()

    @property
    def criado_em(self) -> datetime:
        return self._criado_em

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "paciente_id": self._paciente_id,
            "sintomas": self._sintomas,
            "grau_risco": self._grau_risco.name,
            "cor": self._grau_risco.cor,
            "score": self._grau_risco.score,
            "tempo_maximo_minutos": self._grau_risco.tempo_espera_min,
            "justificativa_ia": self._justificativa_ia,
            "status": self._status,
            "criado_em": self._criado_em.isoformat()
        }

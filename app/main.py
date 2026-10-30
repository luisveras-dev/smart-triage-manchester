from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
from datetime import datetime

from app.models.paciente import Paciente, PacientePreferencial
from app.models.triagem import GrauRisco, Triagem
from app.core.priority_queue import PriorityQueue, ItemFila
from app.database.connection import DatabaseManager
from app.services.ai_service import AIService

# Instâncias Centrais do Sistema (Conexão dos 5 Pilares)
app = FastAPI(
    title="Smart Triage - Protocolo de Manchester",
    description="Sistema Hospitalar Inteligente integrando ED (Min-Heap), BD (SQLite), CRUD, POO e IA (Gemini)",
    version="1.0.0"
)

# Caminhos de Templates e Estáticos
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Instâncias dos Pilares
db = DatabaseManager()
ai_service = AIService()
fila_prioridade = PriorityQueue()


def recarregar_fila_do_banco():
    """
    Restaura a Fila de Prioridade (Min-Heap) em memória com as triagens ativas
    persistidas no SQLite, garantindo resiliência se o servidor reiniciar.
    """
    triagens_ativas = db.listar_triagens_ativas()
    for item in triagens_ativas:
        if item["eh_preferencial"] or item["paciente_idade"] >= 60:
            paciente = PacientePreferencial(
                nome=item["paciente_nome"],
                cpf=item["paciente_cpf"],
                idade=item["paciente_idade"],
                paciente_id=item["paciente_id"]
            )
        else:
            paciente = Paciente(
                nome=item["paciente_nome"],
                cpf=item["paciente_cpf"],
                idade=item["paciente_idade"],
                paciente_id=item["paciente_id"]
            )

        grau = GrauRisco.por_score(item["gravidade_score"])
        triagem = Triagem(
            sintomas=item["sintomas"],
            grau_risco=grau,
            justificativa_ia=item["justificativa_ia"],
            triagem_id=item["triagem_id"],
            paciente_id=item["paciente_id"],
            criado_em=datetime.fromisoformat(item["triagem_criado_em"]) if item["triagem_criado_em"] else None
        )
        fila_prioridade.inserir(ItemFila(paciente, triagem))


# Sincroniza estado inicial do Heap a partir do SQLite
recarregar_fila_do_banco()


# Modelos Pydantic para validação das rotas REST
class AnaliseSintomasRequest(BaseModel):
    sintomas: str
    idade: Optional[int] = 30


class TriagemRequest(BaseModel):
    nome: str
    cpf: str
    idade: int
    eh_preferencial: bool = False
    motivo_preferencia: Optional[str] = "Preferencial por Lei"
    sintomas: str


class AtendimentoRequest(BaseModel):
    triagem_id: int
    medico_responsavel: str
    observacoes: Optional[str] = ""


# --- Rotas da Interface Web ---

@app.get("/", response_class=HTMLResponse)
async def pagina_inicial(request: Request):
    """Serve a interface unificada com as 3 abas."""
    return templates.TemplateResponse(request=request, name="index.html")


# --- Rotas REST (API) ---

@app.post("/api/analisar-sintomas")
async def analisar_sintomas(req: AnaliseSintomasRequest):
    """
    Chama a IA (ou fallback) para pré-visualizar a classificação de Manchester
    sem ainda salvar no banco ou inserir na fila.
    """
    resultado = ai_service.classificar_sintomas(req.sintomas, req.idade)
    return JSONResponse(content=resultado)


@app.post("/api/triagem")
async def criar_triagem(req: TriagemRequest):
    """
    Endpoint principal de triagem:
      1. Instancia os objetos de Domínio (POO).
      2. Classifica gravidade via IA/Fallback (Gemini).
      3. Persiste no SQLite (Banco de Dados + CRUD).
      4. Insere no Min-Heap em tempo real O(log n) (Estrutura de Dados).
    """
    if not req.nome.strip() or not req.cpf.strip() or not req.sintomas.strip():
        raise HTTPException(status_code=400, detail="Nome, CPF e Sintomas são obrigatórios.")

    # 1. POO: Herança e Encapsulamento
    eh_pref = req.eh_preferencial or req.idade >= 60
    if eh_pref:
        motivo = req.motivo_preferencia if req.idade < 60 else "Idoso (>= 60 anos)"
        paciente = PacientePreferencial(
            nome=req.nome,
            cpf=req.cpf,
            idade=req.idade,
            motivo_preferencia=motivo
        )
    else:
        paciente = Paciente(
            nome=req.nome,
            cpf=req.cpf,
            idade=req.idade
        )

    # 2. IA: Classificação pelo Protocolo de Manchester
    analise_ia = ai_service.classificar_sintomas(req.sintomas, req.idade)
    grau_risco = GrauRisco.por_score(analise_ia["score"])

    # 3. BD: CRUD seguro
    paciente_id = db.salvar_paciente(
        nome=paciente.nome,
        cpf=paciente.cpf,
        idade=paciente.idade,
        eh_preferencial=paciente.eh_preferencial
    )
    paciente.id = paciente_id

    triagem_id = db.salvar_triagem(
        paciente_id=paciente_id,
        sintomas=req.sintomas,
        gravidade_score=grau_risco.score,
        cor_manchester=grau_risco.cor,
        tempo_maximo_minutos=grau_risco.tempo_espera_min,
        justificativa_ia=analise_ia["justificativa"]
    )

    triagem = Triagem(
        sintomas=req.sintomas,
        grau_risco=grau_risco,
        justificativa_ia=analise_ia["justificativa"],
        triagem_id=triagem_id,
        paciente_id=paciente_id
    )

    # 4. ED: Inserção no Min-Heap O(log n)
    item_fila = ItemFila(paciente=paciente, triagem=triagem)
    fila_prioridade.inserir(item_fila)

    return JSONResponse(
        content={
            "mensagem": "Paciente triado e inserido na fila com sucesso!",
            "item": item_fila.to_dict(),
            "metodo_ia": analise_ia.get("metodo", "Gemini API")
        },
        status_code=201
    )


@app.get("/api/fila")
async def obter_fila():
    """
    Retorna a fila ordenada pelo Min-Heap manual em tempo real sem alterar a fila.
    """
    elementos = fila_prioridade.listar_elementos()
    lista_dict = [item.to_dict() for item in elementos]

    # Estatísticas rápidas de distribuição por cor
    contagem_cores = {
        "VERMELHO": 0,
        "LARANJA": 0,
        "AMARELO": 0,
        "VERDE": 0,
        "AZUL": 0
    }
    for item in elementos:
        cor = item.triagem.grau_risco.name
        if cor in contagem_cores:
            contagem_cores[cor] += 1

    return JSONResponse(content={
        "total": len(lista_dict),
        "distribuicao": contagem_cores,
        "fila": lista_dict
    })


@app.post("/api/chamar-proximo")
async def chamar_proximo(medico_responsavel: str = Form("Dr(a). Plantonista"), observacoes: str = Form("")):
    """
    Remove o paciente de maior prioridade da raiz do Min-Heap O(log n),
    e registra o atendimento no banco de dados.
    """
    if fila_prioridade.esta_vazia():
        raise HTTPException(status_code=404, detail="Não há pacientes aguardando na fila.")

    proximo_item = fila_prioridade.remover_mais_urgente()
    if not proximo_item:
        raise HTTPException(status_code=404, detail="Fila vazia.")

    # Registra no SQLite
    db.registrar_atendimento(
        triagem_id=proximo_item.triagem.id,
        medico_responsavel=medico_responsavel,
        observacoes=observacoes
    )

    return JSONResponse(content={
        "mensagem": "Paciente chamado com sucesso!",
        "paciente_chamado": proximo_item.to_dict()
    })


@app.get("/api/historico")
async def obter_historico():
    """Retorna a lista dos atendimentos realizados."""
    historico = db.listar_historico_atendimentos(limite=30)
    return JSONResponse(content={"historico": historico})

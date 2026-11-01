import os
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, Any, Optional

# Carrega variáveis de ambiente do arquivo .env da raiz do projeto automaticamente
try:
    from dotenv import load_dotenv
    _raiz_projeto = Path(__file__).resolve().parent.parent.parent
    _env_file = _raiz_projeto / ".env"
    if _env_file.exists():
        load_dotenv(dotenv_path=_env_file)
except Exception:
    pass

# System Prompt Clínico que orienta o modelo de IA sobre o Protocolo de Manchester
CLINICAL_SYSTEM_PROMPT = """Você é um médico regulador especialista em triagem hospitalar atuando sob as diretrizes estritas do Protocolo de Manchester.
Sua missão é analisar os sintomas clínicos relatados e a idade do paciente, determinando o grau de risco e a prioridade de atendimento correspondente.

Categorias do Protocolo de Manchester:
1. VERMELHO (Emergência imediata): Score 1, Tempo máximo de espera: 0 minutos.
   - Indicadores: Risco iminente de morte, parada cardiorrespiratória, choque, trauma penetrante (tiro, facada, perfuração de órgãos vitais), dor torácica aguda com suspeita de infarto, inconsciência, asfixia, hemorragia exanguinante, convulsão ativa.
2. LARANJA (Muito Urgente): Score 2, Tempo máximo de espera: 10 minutos.
   - Indicadores: Dor aguda intensa (EVA 8-10), alteração neurológica aguda (suspeita de AVC), dispneia/falta de ar importante, hemorragia maior incontrolada, queimaduras extensas, fraturas expostas, intoxicações exógenas agudas.
3. AMARELO (Urgente): Score 3, Tempo máximo de espera: 60 minutos.
   - Indicadores: Dor moderada (EVA 4-7), febre alta persistente, vômitos/diarreia incoercíveis com risco de desidratação, dor abdominal aguda moderada, crise de asma leve a moderada, ferimentos profundos.
4. VERDE (Pouco Urgente): Score 4, Tempo máximo de espera: 120 minutos.
   - Indicadores: Condições agudas de baixo risco, dor leve recente (EVA 1-3), sintomas respiratórios superiores (coriza, tosse sem dispneia), contusões leves, escoriações.
5. AZUL (Não Urgente): Score 5, Tempo máximo de espera: 240 minutos.
   - Indicadores: Queixas crônicas estáveis, troca de curativos, renovação de receitas, sintomas antigos sem agravamento agudo.

Diretrizes Obrigatórias de Resposta:
- Você deve responder ESTRITAMENTE em formato JSON válido (RFC 8259).
- Não inclua explicações ou texto conversacional fora do bloco JSON.
- O JSON deve conter EXATAMENTE as seguintes 4 chaves:
{
  "cor": "VERMELHO" | "LARANJA" | "AMARELO" | "VERDE" | "AZUL",
  "score": 1 | 2 | 3 | 4 | 5,
  "justificativa": "Justificativa clínica fundamentada e concisa em 1 ou 2 frases.",
  "tempo_maximo_minutos": 0 | 10 | 60 | 120 | 240
}
"""

# Mapeamento oficial de cores, scores e tempos de espera do Protocolo de Manchester
MANCHESTER_SPECS = {
    "VERMELHO": {"score": 1, "tempo_maximo_minutos": 0},
    "LARANJA": {"score": 2, "tempo_maximo_minutos": 10},
    "AMARELO": {"score": 3, "tempo_maximo_minutos": 60},
    "VERDE": {"score": 4, "tempo_maximo_minutos": 120},
    "AZUL": {"score": 5, "tempo_maximo_minutos": 240},
}


class AIService:
    """
    Serviço de Inteligência Artificial para classificação no Protocolo de Manchester.
    Possui integração com Google Gemini API e Fallback Heurístico Clínico Offline de Alta Resiliência.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[AIService] Aviso ao inicializar google-genai: {e}. Usando fallback.")
                self.client = None

    def classificar_sintomas(self, sintomas: str, idade: int = 30) -> Dict[str, Any]:
        """
        Classifica os sintomas clínicos segundo as diretrizes de Manchester.
        Retorna dicionário padronizado com cor, score, justificativa e tempo_maximo_minutos.
        Garante tolerância a falhas total: nunca lança exceção em caso de queda de API ou rede.
        """
        sintomas_limpos = (sintomas or "").strip()
        if not sintomas_limpos:
            return self._resultado_padrao_azul("Nenhum sintoma relevante relatado.")

        # Tenta classificar via API do Google Gemini se o cliente estiver configurado
        if self.client:
            try:
                return self._classificar_com_gemini(sintomas_limpos, idade)
            except Exception as e:
                print(f"[AIService] Erro na chamada da Gemini API ({e}). Ativando Fallback Heurístico...")

        # Fallback Heurístico Clínico de Emergência (Offline / Blindagem total)
        return self._classificar_com_fallback(sintomas_limpos, idade)

    def _classificar_com_gemini(self, sintomas: str, idade: int) -> Dict[str, Any]:
        """
        Executa a inferência clínica via Google Gemini API usando Structured JSON Output.
        """
        user_prompt = f"""Dados do Paciente:
- Idade: {idade} anos
- Queixa clínica / Sintomas: "{sintomas}"

Analise o quadro acima e determine a classificação estrita no Protocolo de Manchester."""

        # Configura prompt de sistema e formato JSON estrito
        config = None
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=CLINICAL_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.1,
            )
        except Exception:
            pass

        # Monta chamada com ou sem o objeto de configuração do SDK
        kwargs = {
            "model": self.model,
            "contents": f"{CLINICAL_SYSTEM_PROMPT}\n\n{user_prompt}" if config is None else user_prompt,
        }
        if config is not None:
            kwargs["config"] = config

        response = self.client.models.generate_content(**kwargs)
        texto_resposta = getattr(response, "text", "") or ""
        return self._parse_resposta_json(texto_resposta)

    def _parse_resposta_json(self, texto: str) -> Dict[str, Any]:
        """
        Extrai e valida o JSON da resposta gerada pela IA.
        Remove blocos de código Markdown (```json ... ```) se presentes
        e garante a coerência dos campos segundo a especificação de Manchester.
        """
        texto_limpo = texto.strip()

        # Remove formatação de bloco de código markdown caso o modelo tenha incluído
        if texto_limpo.startswith("```"):
            texto_limpo = re.sub(r"^```(?:json)?\s*", "", texto_limpo, flags=re.IGNORECASE)
            texto_limpo = re.sub(r"\s*```$", "", texto_limpo)

        match = re.search(r"\{.*\}", texto_limpo, re.DOTALL)
        if not match:
            raise ValueError(f"Resposta da IA não contém bloco JSON válido: '{texto[:100]}'")

        dados = json.loads(match.group(0))

        cor = str(dados.get("cor", "")).strip().upper()
        if cor not in MANCHESTER_SPECS:
            raise ValueError(f"Cor inválida retornada pela IA: '{cor}'")

        specs = MANCHESTER_SPECS[cor]
        score = int(dados.get("score", specs["score"]))
        tempo = int(dados.get("tempo_maximo_minutos", specs["tempo_maximo_minutos"]))
        justificativa = str(dados.get("justificativa", "Classificação clínica baseada no Protocolo de Manchester.")).strip()

        # Garante consistência dos dados com o protocolo
        if score != specs["score"]:
            score = specs["score"]
        if tempo != specs["tempo_maximo_minutos"]:
            tempo = specs["tempo_maximo_minutos"]

        metodo_desc = "Gemini 2.5 Flash (IA Generativa)" if "2.5" in self.model else f"Gemini {self.model} (IA Generativa)"

        return {
            "cor": cor,
            "score": score,
            "justificativa": justificativa,
            "tempo_maximo_minutos": tempo,
            "metodo": metodo_desc
        }

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        """
        Remove acentos ortográficos e converte para minúsculas
        para comparação léxica robusta e tolerante a variações do usuário.
        """
        normalizado = unicodedata.normalize("NFKD", texto or "")
        sem_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
        return sem_acentos.lower()

    def _classificar_com_fallback(self, sintomas: str, idade: int) -> Dict[str, Any]:
        """
        Analisador Léxico-Clínico Heurístico Local.
        Garante blindagem total da aplicação caso a API esteja indisponível, sem cota,
        sem chave configurada ou em ambiente de apresentação presencial sem internet.
        """
        texto = self._normalizar_texto(sintomas)

        # 1. Vermelho - Risco iminente de morte / Parada / Infarto / Trauma Penetrante / Asfixia / Choque
        termos_vermelho = [
            # Traumas graves e perfurantes (tiro, facada, armas, etc.)
            "tiro", "baleado", "bala", "arma de fogo", "paf", "facada", "esfaqueado",
            "arma branca", "alojado", "alojada", "perfuracao", "estilhaco", "evisceracao",
            "amputacao", "politrauma", "atropelamento grave", "esmagamento",
            # Parada, respiração e consciência
            "dor no peito", "aperto no peito", "queimacao no peito", "dor toracica", "infarto",
            "parada", "sem pulso", "inconsciente", "nao respira", "parou de respirar",
            "dificuldade para respirar grave", "asfixia", "afogamento", "enforcamento",
            "choque", "desmaiado", "desmaio", "coma", "cianose", "labios roxos",
            # Hemorragias extremas e crises agudas
            "hemorragia grave", "hemorragia macica", "sangrando muito", "esvaindo em sangue",
            "hemorragia incontrolada", "convulsao ativa", "convulsao", "convulsionando",
            "anafilaxia", "edema de glote", "glote fechando"
        ]
        if any(termo in texto for termo in termos_vermelho):
            return {
                "cor": "VERMELHO",
                "score": 1,
                "justificativa": "Emergência imediata com risco iminente à vida ou trauma penetrante crítico identificado pelo analisador clínico de emergência.",
                "tempo_maximo_minutos": 0,
                "metodo": "Fallback Clínico Heurístico (Offline)"
            }

        # 2. Laranja - Muito Urgente
        termos_laranja = [
            # Fraturas, queimaduras e sangramentos ativos
            "fratura exposta", "osso exposto", "queimadura grave", "queimadura extensa",
            "sangramento ativo", "hemorragia", "ferimento extenso",
            # Respiratório e Neurológico
            "falta de ar", "dificuldade para respirar", "dispneia", "sufocando",
            "avc", "derrame", "perda de forca", "paralisia", "boca torta", "fala enrolada",
            "cefaleia subita", "dor de cabeca explosiva", "alteracao neurologica",
            # Hipertensão severa, intoxicações e dores intensas
            "pressao 20", "pressao muito alta", "pressao alta severa", "crise hipertensiva",
            "intoxicacao", "veneno", "overdose", "picada de cobra", "escorpiao",
            "dor intensa", "dor insuportavel", "dor 10", "dor severa",
            "febre em recem-nascido", "bebe com febre"
        ]
        if any(termo in texto for termo in termos_laranja):
            return {
                "cor": "LARANJA",
                "score": 2,
                "justificativa": "Condição aguda de alta gravidade com potencial de deterioração rápida.",
                "tempo_maximo_minutos": 10,
                "metodo": "Fallback Clínico Heurístico (Offline)"
            }

        # 3. Amarelo - Urgente
        termos_amarelo = [
            "dor moderada", "febre alta", "39 graus", "40 graus", "febre persistente",
            "vomito constante", "vomitos frequentes", "vomitando muito", "vomito", "vomitos",
            "diarreia aguda", "diarreia intensa", "diarreia frequente",
            "tontura forte", "vertigem", "colica renal", "pedra no rim",
            "crise de asma", "chiado no peito", "ferimento profundo", "corte profundo",
            "dor abdominal", "dor na barriga", "dor de estomago", "desidratacao",
            "crise de ansiedade", "panico", "palpitacao"
        ]
        if any(termo in texto for termo in termos_amarelo):
            return {
                "cor": "AMARELO",
                "score": 3,
                "justificativa": "Quadro clínico que exige investigação médica em curto prazo.",
                "tempo_maximo_minutos": 60,
                "metodo": "Fallback Clínico Heurístico (Offline)"
            }

        # 4. Verde - Pouco Urgente
        termos_verde = [
            "dor leve", "entorse", "torcao", "resfriado", "gripe", "tosse", "coriza",
            "garganta inflamada", "dor de garganta", "escoriacao", "ralado", "arranhado",
            "unha encravada", "pequeno corte", "corte superficial", "dor muscular",
            "azia", "enjoo leve", "mal-estar leve"
        ]
        if any(termo in texto for termo in termos_verde):
            return {
                "cor": "VERDE",
                "score": 4,
                "justificativa": "Condição de baixa complexidade passível de aguardo sem risco iminente.",
                "tempo_maximo_minutos": 120,
                "metodo": "Fallback Clínico Heurístico (Offline)"
            }

        # 5. Azul - Não Urgente (Padrão para queixas leves ou crônicas)
        return self._resultado_padrao_azul("Sintomas leves ou quadro crônico sem indícios de urgência imediata.")

    def _resultado_padrao_azul(self, justificativa: str) -> Dict[str, Any]:
        """Gera resposta padronizada para classificação Azul."""
        return {
            "cor": "AZUL",
            "score": 5,
            "justificativa": justificativa,
            "tempo_maximo_minutos": 240,
            "metodo": "Fallback Clínico Heurístico (Offline)"
        }

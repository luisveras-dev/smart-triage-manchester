import os
import json
import re
from typing import Dict, Any


class AIService:
    """
    Serviço de Inteligência Artificial para classificação no Protocolo de Manchester.
    Possui integração com Google Gemini API e Fallback Heurístico Clínico Offline.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
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
        """
        sintomas_limpos = (sintomas or "").strip()
        if not sintomas_limpos:
            return self._resultado_padrao_azul("Nenhum sintoma relevante relatado.")

        # Tenta usar a API do Google Gemini se disponível
        if self.client:
            try:
                return self._classificar_com_gemini(sintomas_limpos, idade)
            except Exception as e:
                print(f"[AIService] Erro na chamada da Gemini API ({e}). Ativando Fallback Heurístico...")

        # Fallback Heurístico Clínico de Emergência
        return self._classificar_com_fallback(sintomas_limpos, idade)

    def _classificar_com_gemini(self, sintomas: str, idade: int) -> Dict[str, Any]:
        prompt = f"""
Você é um médico especialista em triagem hospitalar atuando sob o estrito Protocolo de Manchester.
Analise a queixa e sintomas do paciente abaixo e classifique-o em uma das 5 categorias de Manchester:
1. VERMELHO: Emergência imediata (Score 1, 0 min) - Risco iminente de morte, parada, choque, dor torácica aguda/infarto, inconsciência.
2. LARANJA: Muito Urgente (Score 2, 10 min) - Dor severa aguda, alteração neurológica súbita, hemorragia maior, dispneia importante.
3. AMARELO: Urgente (Score 3, 60 min) - Dor moderada, febre alta persistente, vômitos incoercíveis, desidratação leve a moderada.
4. VERDE: Pouco Urgente (Score 4, 120 min) - Condições agudas de baixo risco, dor leve, sintomas respiratórios leves sem dispneia.
5. AZUL: Não Urgente (Score 5, 240 min) - Queixas crônicas, troca de curativos, consultas de rotina.

Dados do Paciente:
- Idade: {idade} anos
- Queixa clínica / Sintomas: "{sintomas}"

Responda OBRIGATORIAMENTE em JSON válido, com a seguinte estrutura:
{{
  "cor": "VERMELHO" | "LARANJA" | "AMARELO" | "VERDE" | "AZUL",
  "score": 1 | 2 | 3 | 4 | 5,
  "justificativa": "breve justificativa clínica médica fundamentada em 1 ou 2 frases",
  "tempo_maximo_minutos": 0 | 10 | 60 | 120 | 240
}}
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        texto = response.text.strip()
        # Limpa blocos markdown de json
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            dados = json.loads(match.group(0))
            return {
                "cor": str(dados.get("cor", "AZUL")).upper(),
                "score": int(dados.get("score", 5)),
                "justificativa": str(dados.get("justificativa", "Análise realizada via Gemini IA.")),
                "tempo_maximo_minutos": int(dados.get("tempo_maximo_minutos", 240)),
                "metodo": "Gemini 2.5 Flash (IA Generativa)"
            }
        raise ValueError("Resposta da IA não contém JSON válido.")

    def _classificar_com_fallback(self, sintomas: str, idade: int) -> Dict[str, Any]:
        """
        Analisador Léxico-Clínico Heurístico.
        Garante blindagem total durante apresentações presenciais sem internet.
        """
        texto = sintomas.lower()

        # 1. Vermelho - Risco de morte / Parada / Infarto / Asfixia
        termos_vermelho = [
            "dor no peito", "infarto", "parada", "inconsciente", "não respira",
            "choque", "desmaiado", "hemorragia grave", "convulsão ativa", "asfixia",
            "anafilaxia", "cianose", "coma"
        ]
        if any(termo in texto for termo in termos_vermelho):
            return {
                "cor": "VERMELHO",
                "score": 1,
                "justificativa": "Sintomas críticos indicativos de risco imediato à vida identificados pelo analisador clínico de emergência.",
                "tempo_maximo_minutos": 0,
                "metodo": "Fallback Clínico Heurístico (Offline)"
            }

        # 2. Laranja - Muito Urgente
        termos_laranja = [
            "dor intensa", "fratura exposta", "queimadura grave", "falta de ar",
            "dificuldade para respirar", "cefaleia súbita", "avc", "paralisia",
            "perda de força", "sangramento ativo", "pressão 20", "febre em recém-nascido"
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
            "dor moderada", "febre alta", "vômito constante", "vômitos frequentes",
            "diarreia aguda", "tontura forte", "cólica renal", "crise de asma leve",
            "ferimento profundo", "dor abdominal", "crise de ansiedade"
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
            "dor leve", "entorse", "resfriado", "tosse", "coriza", "garganta inflamada",
            "escoriação", "ralado", "unha encravada", "dor muscular", "azia"
        ]
        if any(termo in texto for termo in termos_verde):
            return {
                "cor": "VERDE",
                "score": 4,
                "justificativa": "Condição de baixa complexidade passível de aguardo sem risco iminente.",
                "tempo_maximo_minutos": 120,
                "metodo": "Fallback Clínico Heurístico (Offline)"
            }

        # 5. Azul - Não Urgente (Padrão)
        return self._resultado_padrao_azul("Sintomas leves ou quadro crônico sem indícios de urgência imediata.")

    def _resultado_padrao_azul(self, justificativa: str) -> Dict[str, Any]:
        return {
            "cor": "AZUL",
            "score": 5,
            "justificativa": justificativa,
            "tempo_maximo_minutos": 240,
            "metodo": "Fallback Clínico Heurístico (Offline)"
        }

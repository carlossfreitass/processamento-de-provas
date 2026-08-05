"""
Módulo de classificação por IA — valida os resultados da FSM usando a API da Groq.
"""

import os
import hashlib
from bs4 import BeautifulSoup
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GROQ_API_KEY")
client = None
if _api_key:
    client = Groq(api_key=_api_key)

_cache = {}

def _hash_text(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def classify_with_ai(block_html: str) -> str:
    """
    Usa a API da Groq para classificar se o texto de uma questão
    é MULTIPLA escolha ou DISCURSIVA, servindo como validador para a FSM.
    """
    # Extrair texto plano
    soup = BeautifulSoup(block_html, "html.parser")
    plain_text = soup.get_text(separator="\n", strip=True)

    # Verificar cache
    text_hash = _hash_text(plain_text)
    if text_hash in _cache:
        return _cache[text_hash]

    if not client:
        print("[AI Classifier] AVISO: GROQ_API_KEY não configurada. Fallback para FSM.")
        return "ERROR"

    # Mensagens do sistema para restrição máxima
    system_prompt = """Você é um assistente especialista em processamento e estruturação de avaliações escolares.
Sua tarefa é ler o conteúdo HTML de uma questão e classificá-la estritamente como "MULTIPLA" ou "DISCURSIVA".

REGRAS DE CLASSIFICAÇÃO:
1. MULTIPLA: A questão apresenta opções onde o aluno deve escolher apenas UMA resposta correta. As opções geralmente completam uma frase ou são afirmações fechadas.
2. DISCURSIVA: O aluno precisa escrever, calcular ou desenhar a resposta.

ATENÇÃO PARA O FALSO POSITIVO:
Questões discursivas frequentemente usam letras (a, b, c, d) para separar subitens ou perguntas múltiplas. 
Se os itens iniciados por letras contiverem verbos de comando imperativos (ex: "Calcule...", "Determine...", "Explique...", "Justifique...", "Por que..."), a questão é DISCURSIVA e não múltipla escolha.

Responda APENAS com a palavra MULTIPLA ou DISCURSIVA, sem pontuação ou texto adicional."""
    
    user_prompt = f"Conteúdo HTML da Questão:\n{block_html}"
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=5,
        )
        
        answer = chat_completion.choices[0].message.content.strip().upper()
        
        if "MULTIPLA" in answer:
            res = "MULTIPLA"
        elif "DISCURSIVA" in answer:
            res = "DISCURSIVA"
        else:
            print(f"[AI Classifier] AVISO: Resposta inesperada da Groq: '{answer}'. Fallback para FSM.")
            res = "ERROR"
            
        _cache[text_hash] = res
        return res
        
    except Exception as e:
        print(f"[AI Classifier] ERRO ao chamar API da Groq: {str(e)}. Fallback para FSM.")
        return "ERROR"
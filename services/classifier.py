"""
Módulo de classificação — divide o HTML em questões e classifica via Máquina de Estados Finita (FSM).
"""

import re
from bs4 import BeautifulSoup

def split_into_blocks(sanitized_html: str) -> list[str]:
    """
    Divide o texto em blocos, um por questão.
    Procura por padrões de numeração no início de parágrafos/headings.
    """
    if not sanitized_html:
        return []

    # Regex para identificar o início de uma questão
    pattern = re.compile(
        r'(<p[^>]*>|<h[1-6][^>]*>)\s*(?:<(?:b|strong|span)[^>]*>\s*)*'
        r'(?:Quest[ãa]o\s+)?(\d+)\s*(?:[\.\)\-]|&ndash;|&mdash;|—)?\s*'
        r'(?:</(?:b|strong|span)>\s*)*',
        re.IGNORECASE | re.DOTALL
    )

    matches = list(pattern.finditer(sanitized_html))

    if not matches:
        # Se não encontrou marcação explícita de questão, trata o HTML inteiro como 1 bloco
        return [sanitized_html]

    blocks = []

    # Trata caso onde há texto antes da primeira questão
    first_match_start = matches[0].start()
    if first_match_start > 0:
        intro = sanitized_html[0:first_match_start].strip()
        pass

    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i + 1 < len(matches) else len(sanitized_html)
        blocks.append(sanitized_html[start:end].strip())

    return blocks

def classify_question(block: str) -> dict:
    """
    FSM que classifica o bloco em 'multipla_escolha' ou 'discursiva' e extrai alternativas.
    """
    # Extrair o número da questão do bloco
    numero = 0
    num_pattern = re.search(r'(?:Quest[ãa]o\s+)?(\d+)\s*(?:[\.\)\-]|&ndash;|&mdash;|—)?\s*', block, re.IGNORECASE)
    if num_pattern:
        numero = int(num_pattern.group(1))

    # Parseia o bloco inteiro
    soup = BeautifulSoup(block, 'html.parser')

    # Máquina de Estados Finita (FSM)
    # Estados: 'ENUNCIADO', 'ALTERNATIVAS'
    estado = 'ENUNCIADO'

    enunciado_html = []
    alternativas = []

    current_alt_letter = None
    current_alt_html = []

    # Regex para identificar alternativas: A), B., (C), d) etc no início do texto do elemento
    alt_pattern = re.compile(r'^\s*\(?([A-Ea-e])\)[\.\)]?\s+(.*)', re.DOTALL)
    alt_pattern_dot = re.compile(r'^\s*([A-Ea-e])\.\s+(.*)', re.DOTALL)

    # Itera sobre os elementos de nível superior ou quase superior
    for element in soup.contents:
        if isinstance(element, str):
            text_str = element.strip()
            if not text_str:
                continue
            is_match = None
        else:
            if element.name in ['br', 'hr']:
                if estado == 'ENUNCIADO':
                    enunciado_html.append(str(element))
                else:
                    current_alt_html.append(str(element))
                continue

            text_str = element.get_text(separator=" ", strip=True)

        match = alt_pattern.match(text_str) or alt_pattern_dot.match(text_str)

        is_alternative = False
        letter = None

        if match:
            letter = match.group(1).upper()
            # Valida sequência
            if estado == 'ENUNCIADO' and letter == 'A':
                is_alternative = True
            elif estado == 'ALTERNATIVAS':
                if letter in ['A', 'B', 'C', 'D', 'E']:
                    is_alternative = True

        if element.name == 'li' and not is_alternative:
            pass

        if is_alternative:
            if estado == 'ENUNCIADO':
                estado = 'ALTERNATIVAS'
            elif estado == 'ALTERNATIVAS':
                # Salva a alternativa anterior
                if current_alt_letter:
                    # Limpa o HTML da alternativa para tirar a letra do começo se possível
                    alt_html_str = "".join(current_alt_html).strip()
                    alternativas.append({"letra": current_alt_letter, "texto": alt_html_str})

            current_alt_letter = letter
            current_alt_html = [str(element)]
        else:
            if estado == 'ENUNCIADO':
                enunciado_html.append(str(element))
            elif estado == 'ALTERNATIVAS':
                current_alt_html.append(str(element))

    # Salva a última alternativa, se houver
    if estado == 'ALTERNATIVAS' and current_alt_letter:
        alt_html_str = "".join(current_alt_html).strip()
        alternativas.append({"letra": current_alt_letter, "texto": alt_html_str})

    tipo = "multipla_escolha" if len(alternativas) > 0 else "discursiva"

    return {
        "numero": numero,
        "tipo": tipo,
        "enunciado": "".join(enunciado_html).strip(),
        "alternativas": alternativas
    }
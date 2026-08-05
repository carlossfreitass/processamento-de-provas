"""
Serviço de parsing — extração e transformação de dados de provas.
"""

from services.sanitizer import sanitize_html, extract_and_tokenize_images, reinject_images
from services.classifier import split_into_blocks, classify_question

def parse_input(raw_html: str) -> dict:
    """
    Orquestra o pipeline completo:
    1. Sanitiza o HTML
    2. Extrai imagens Base64
    3. Divide em blocos
    4. Classifica as questões
    5. Reinjeta imagens
    """
    if not raw_html:
        raise ValueError("HTML vazio fornecido para processamento.")

    try:
        # Sanitização
        clean_html = sanitize_html(raw_html)

        # Tokenização de imagens
        tokenized_html, image_map = extract_and_tokenize_images(clean_html)

        # Divisão em Blocos
        blocks = split_into_blocks(tokenized_html)

        # Classificação
        questoes = []
        for block in blocks:
            questao = classify_question(block)

            # Reinjeção de imagens em cada componente do JSON
            questao["enunciado"] = reinject_images(questao["enunciado"], image_map)
            for alt in questao["alternativas"]:
                alt["texto"] = reinject_images(alt["texto"], image_map)

            questoes.append(questao)

        return {
            "total_questoes": len(questoes),
            "questoes": questoes
        }

    except Exception as e:
        raise RuntimeError(f"Erro no pipeline de parsing: {str(e)}")
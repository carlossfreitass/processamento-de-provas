"""
Módulo de sanitização — limpeza de HTML sujo e extração de imagens.
"""

import re
from bs4 import BeautifulSoup

def sanitize_html(raw_html: str) -> str:
    """
    Limpa o HTML removendo atributos irrelevantes, spans vazios e parágrafos sem conteúdo,
    preservando a estrutura e formatação semântica útil.
    """
    if not raw_html:
        return ""

    # html.parser
    soup = BeautifulSoup(raw_html, "html.parser")

    # Tags e atributos permitidos
    allowed_tags = {
        "p", "br", "strong", "b", "em", "i", "u",
        "ul", "ol", "li", "img", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"
    }
    
    # Remover atributos indesejados
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags and tag.name != "span":
            tag.unwrap()
            continue

        allowed_attrs = ["src"] if tag.name == "img" else []
        attrs_to_remove = [attr for attr in tag.attrs if attr not in allowed_attrs]
        for attr in attrs_to_remove:
            del tag[attr]

    # Desaninhar e remover spans
    for span in soup.find_all("span"):
        span.unwrap()

    # Remover parágrafos vazios ou apenas com espaços/br
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        imgs = p.find_all("img")
        if not text and not imgs:
            p.decompose()

    # Converte de volta para string
    cleaned = str(soup)

    # Normalizar quebras de linha excessivas (regex)
    cleaned = cleaned.strip()

    return cleaned

def extract_and_tokenize_images(html: str) -> tuple[str, dict]:
    """
    Extrai tags <img> contendo Base64, substituindo por tokens no HTML.
    Retorna o HTML com os tokens e um dicionário de { token: tag_img_completa }.
    """
    if not html:
        return html, {}

    soup = BeautifulSoup(html, "html.parser")
    image_map = {}

    # Busca todas as tags img
    for idx, img in enumerate(soup.find_all("img")):
        token = f"[[IMG_TOKEN_{idx}]]"
        image_map[token] = str(img)
        # Substitui a tag img no DOM pelo token
        img.replace_with(token)

    return str(soup), image_map

def reinject_images(html: str, image_map: dict) -> str:
    """
    Substitui os tokens de imagem de volta pelas tags <img> originais.
    """
    if not html or not image_map:
        return html

    for token, img_tag in image_map.items():
        # Usa replace simples na string
        html = html.replace(token, img_tag)

    return html
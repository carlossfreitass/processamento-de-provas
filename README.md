<div align="center">

<h1>
  <img src="https://img.shields.io/badge/PROCESSAMENTO%20DE%20PROVAS-Pipeline%20Inteligente-6366f1?style=for-the-badge&logoColor=white" alt="Processamento de Provas"/>
</h1>

<p align="center">
  <strong>Parsing automatizado de avaliações escolares com IA — extrai questões, imagens e alternativas de qualquer prova colada diretamente do Word ou Google Docs.</strong>
</p>

<br/>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Groq-LLaMA%203.1-F55036?style=flat-square&logo=meta&logoColor=white" alt="Groq"/>
  <img src="https://img.shields.io/badge/Quill.js-2.0-06B6D4?style=flat-square&logo=javascript&logoColor=white" alt="Quill.js"/>
  <img src="https://img.shields.io/badge/BeautifulSoup-4.13-3776AB?style=flat-square&logo=python&logoColor=white" alt="BeautifulSoup"/>
</p>

</div>

---

## Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Pipeline de Funcionamento](#-pipeline-de-funcionamento)
- [Tecnologias](#-tecnologias)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação Local](#-instalação-local)
- [Executando a Aplicação](#-executando-a-aplicação)
- [Rotas da API](#-rotas-da-api)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)

---

## Sobre o Projeto

O **Processamento de Provas** é uma aplicação web que automatiza o processo de digitalização e estruturação de avaliações escolares. Professores colam o conteúdo de uma prova (diretamente do Word, Google Docs ou como texto formatado) em um editor rich-text integrado, e a aplicação executa um pipeline inteligente de 5 etapas para transformar aquele conteúdo bruto em um JSON estruturado, pronto para uso em sistemas de gestão de avaliações.

**Problema que resolve:**
Provas digitadas no Word ou Google Docs chegam repletas de ruído: estilos inline, `<span>` aninhados, imagens como blobs temporários, numerações inconsistentes. Digitalizar isso manualmente é custoso e sujeito a erros.

**Como o Processamento de Provas resolve:**
- Limpa e normaliza o HTML colado via BeautifulSoup.
- Tokeniza imagens Base64 para não poluir o fluxo de texto.
- Divide o conteúdo em questões individuais via RegEx inteligente.
- Classifica cada questão (múltipla escolha × discursiva) com uma FSM de estados, validada por um modelo LLM via API da Groq.
- Reinjeta as imagens nos campos corretos do JSON de saída.

---

## Pipeline de Funcionamento

```
Cole a Prova (Quill.js)
        │
        ▼
 [1] sanitize_html()          ← Remove ruído CSS/HTML (BeautifulSoup)
        │
        ▼
 [2] extract_and_tokenize_images()  ← Base64 → [[IMG_TOKEN_X]]
        │
        ▼
 [3] split_into_blocks()      ← Divide por numeração de questão (RegEx)
        │
        ▼
 [4] classify_question() (FSM)
        │ se detectar múltipla escolha
        ▼
 [4b] classify_with_ai()      ← Validação via Groq (llama-3.1-8b-instant)
        │
        ▼
 [5] reinject_images()        ← Restaura [[IMG_TOKEN_X]] → Base64
        │
        ▼
  JSON estruturado { questoes: [...] }
```

---

## Tecnologias

| Tecnologia | Versão | Função |
|---|---|---|
| **Python** | 3.11+ | Linguagem principal do backend |
| **Flask** | 3.1.x | Framework web — servidor, rotas e blueprints |
| **flask-cors** | 5.0.x | Habilita CORS para chamadas do frontend em dev |
| **BeautifulSoup4** | 4.13.x | Parser e sanitizador de HTML |
| **groq** | 1.6.x | SDK oficial da Groq — integração com LLaMA 3.1 |
| **python-dotenv** | 1.1.x | Carregamento de variáveis de ambiente do `.env` |
| **Quill.js** | 2.0 (CDN) | Editor rich-text no frontend com suporte a imagens |
| **Jinja2** | (via Flask) | Renderização de templates HTML |
| **Vanilla JS** | ES2022 | Lógica de interface, paste handler e fetch da API |

---

## Estrutura do Projeto

```
processamento-de-provas/
│
├── app.py                   # Ponto de entrada — Application Factory do Flask
│
├── app_routes/              # Blueprints de rotas (separação de responsabilidades)
│   ├── health.py            # GET /health — healthcheck da aplicação
│   ├── input.py             # POST /input — entrada do pipeline de parsing
│   └── pages.py             # GET / — serve a interface web (index.html)
│
├── services/                # Camada de negócio e integração com IA
│   ├── sanitizer.py         # Fase 2: Limpeza de HTML e tokenização de imagens
│   ├── classifier.py        # Fase 3: FSM de divisão e classificação de questões
│   ├── ai_classifier.py     # Fase 3b: Validação por IA via API Groq (com cache e fallback)
│   └── parser.py            # Orquestrador do pipeline completo (Fases 1→5)
│
├── templates/
│   └── index.html           # Interface web completa: editor Quill + painel de resultados
│
├── .env                     # Variáveis de ambiente locais (não comitar — ver .gitignore)
├── .env.example             # Template de variáveis de ambiente
├── requirements.txt         # Dependências Python do projeto
└── .gitignore
```

---

## Instalação Local

### Pré-requisitos

- Python **3.11 ou superior**
- `pip` atualizado
- Uma chave de API da [Groq](https://console.groq.com) (gratuita)

### Passo a Passo

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/processamento-de-provas.git
cd processamento-de-provas
```

**2. Crie e ative o ambiente virtual**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto (copie o template `.env.example`):

```bash
cp .env.example .env
```

Edite o arquivo `.env` e preencha sua chave da Groq:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> Obtenha sua chave gratuitamente em [console.groq.com](https://console.groq.com/keys).

---

## Executando a Aplicação

Com o ambiente virtual ativado e o `.env` configurado, execute:

```bash
flask run --port 5000
```

ou diretamente:

```bash
python app.py
```

Acesse a interface em: **[http://localhost:5000](http://localhost:5000)**

---

## Rotas da API

### `GET /`
Serve a interface web principal — o editor rich-text Quill.js e o painel de resultados com as abas **Prova Formatada** e **JSON Bruto**.

---

### `GET /health`
Healthcheck da aplicação.

**Resposta:**
```json
{ "status": "ok" }
```

---

### `POST /input`
Endpoint principal do pipeline de parsing. Recebe o HTML do editor e devolve o JSON estruturado com todas as questões identificadas.

**Request:**
```http
POST /input
Content-Type: application/json

{
  "html": "<p>1. Qual é a capital do Brasil?</p><p>A) São Paulo</p><p>B) Brasília</p>..."
}
```

**Response (200 OK):**
```json
{
  "total_questoes": 2,
  "questoes": [
    {
      "numero": 1,
      "tipo": "multipla_escolha",
      "enunciado": "<p>Qual é a capital do Brasil?</p>",
      "alternativas": [
        { "letra": "A", "texto": "<p>São Paulo</p>" },
        { "letra": "B", "texto": "<p>Brasília</p>" }
      ]
    },
    {
      "numero": 2,
      "tipo": "discursiva",
      "enunciado": "<p>Explique o processo de fotossíntese.</p>",
      "alternativas": []
    }
  ]
}
```

**Response (400/500):**
```json
{
  "error": "Descrição do erro ocorrido no pipeline."
}
```

---

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `GROQ_API_KEY` | **Sim** (para IA) | Chave de API da Groq. Sem ela, o classificador cai no fallback FSM automaticamente — a aplicação ainda funciona, mas sem validação por IA. |

> **Nota sobre o Fallback:** O sistema é resiliente por design. Se a `GROQ_API_KEY` não estiver configurada, ou se a API da Groq falhar (timeout, erro 429, etc.), o módulo `ai_classifier.py` registra um aviso no console e delega a decisão final para a FSM local — **o pipeline nunca quebra por causa da IA**.
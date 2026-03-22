# Referências Cruzadas da Bíblia

Projeto de análise e visualização da rede de referências cruzadas da Bíblia (padrão NVI).

## Estrutura

- **Scripts Python:** Geração de CSV, análise topológica, preparação de dados para webapp
- **Webapp React:** Visualização interativa com Sigma.js (WebGL), otimizada para mobile

## Fonte dos Dados

- **OpenBible.info** – Dataset com ~340 mil referências cruzadas
- Download automático: `https://a.openbible.info/data/cross-references.zip`

## Setup Inicial

```bash
# 1. Gerar CSV de referências
python3 gerar_referencias_biblicas.py

# 2. Calcular métricas topológicas
python3 analise_topologica_biblia.py

# 3. Preparar dados para a webapp
python3 preparar_dados_webapp.py
```

## Webapp (Docker)

```bash
# Construir e subir (porta 9995)
docker compose up --build

# Aceder: http://localhost:9995
```

**Nota:** Execute `preparar_dados_webapp.py` antes do build para gerar os ficheiros em `webapp/public/data/`.

## Desenvolvimento Local

```bash
cd webapp
npm install
npm run dev
```

## Estrutura do CSV

| Coluna | Descrição |
|--------|-----------|
| `source` | Versículo de origem (ex: Gênesis 1:1) |
| `target` | Versículo referenciado (ex: João 1:1) |

Formato: `Nome do Livro Capítulo:Versículo`

## Análise Topológica

Para calcular métricas e gerar visualização:

```bash
source venv/bin/activate
pip install -r requirements.txt
python analise_topologica_biblia.py
```

**Saídas:**
- `metricas_topologicas_biblia.csv` – Degree, Eigenvector e Betweenness por versículo
- `grafo_referencias_biblia.png` – Visualização (tamanho = Eigenvector, cor = Betweenness)

**Otimizações:** Betweenness usa amostragem `k=1000`; visualização usa subgrafo dos top 300 nós.

## Uso no Cytoscape

1. **Importar rede:** `referencias_nvi_cytoscape.csv` (source/target)
2. **Importar atributos:** `metricas_topologicas_biblia.csv` como *Node Table* (mapear por versículo)
3. **Tipo:** *Directed*
4. **Layouts:** *Prefuse Force Directed* ou *yFiles Organic Layout*

## Mapeamento de Livros

O script converte automaticamente as abreviações em inglês do OpenBible para os nomes completos em português NVI (ex: Gen → Gênesis, Rev → Apocalipse).

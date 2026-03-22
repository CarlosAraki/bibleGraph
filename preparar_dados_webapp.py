#!/usr/bin/env python3
"""
Prepara os dados CSV para o formato JSON (graphology) consumido pela webapp.
Gera: graph_full.json, graph_top500.json, verses_autocomplete.json
"""

import json
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).parent.resolve()
CSV_EDGES = SCRIPT_DIR / "referencias_nvi_cytoscape.csv"
CSV_METRICS = SCRIPT_DIR / "metricas_topologicas_biblia.csv"
OUTPUT_DIR = SCRIPT_DIR / "webapp" / "public" / "data"

# Livros do Antigo Testamento (para coloração semântica)
LIVROS_AT = {
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute",
    "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras",
    "Neemias", "Ester", "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cânticos",
    "Isaías", "Jeremias", "Lamentações", "Ezequiel", "Daniel", "Oseias", "Joel",
    "Amós", "Obadias", "Jonas", "Miquéias", "Naum", "Habacuque", "Sofonias",
    "Ageu", "Zacarias", "Malaquias",
}


def get_book_type(versiculo: str) -> str:
    """Retorna 'OT' ou 'NT' baseado no livro."""
    parts = versiculo.split()
    if not parts:
        return "OT"
    livro = parts[0]
    if livro in ("1", "2", "3") and len(parts) >= 2:
        livro = f"{livro} {parts[1]}"
    return "OT" if livro in LIVROS_AT else "NT"


def hex_color(book_type: str, betweenness_norm: float) -> str:
    """Cores: AT=tons azul, NT=tons laranja. Intensidade por betweenness."""
    base = 0.3 + betweenness_norm * 0.7
    if book_type == "OT":
        r, g, b = int(59 * base), int(130 * base), int(246 * base)
    else:
        r, g, b = int(249 * base), int(115 * base), int(22 * base)
    return f"#{r:02x}{g:02x}{b:02x}"


def build_graph_data(edges_df: pd.DataFrame, metrics_df: pd.DataFrame, top_n: int | None = None) -> dict:
    """Constrói o grafo no formato graphology."""
    import random
    random.seed(42)

    metrics = metrics_df.set_index("versiculo")
    if top_n:
        top_verses = set(metrics_df.nlargest(top_n, "betweenness_centrality")["versiculo"].tolist())
        edges_df = edges_df[
            edges_df["source"].isin(top_verses) & edges_df["target"].isin(top_verses)
        ]

    all_nodes = list(set(edges_df["source"].tolist() + edges_df["target"].tolist()))
    betweenness_max = metrics_df["betweenness_centrality"].max()
    eigenvector_max = metrics_df["eigenvector_centrality"].max()

    nodes = []
    for i, v in enumerate(all_nodes):
        row = metrics.loc[v] if v in metrics.index else None
        betweenness_norm = row["betweenness_centrality"] / betweenness_max if row is not None and betweenness_max > 0 else 0
        eigenvector_norm = row["eigenvector_centrality"] / eigenvector_max if row is not None and eigenvector_max > 0 else 0
        book_type = get_book_type(v)
        size = 3 + eigenvector_norm * 8
        nodes.append({
            "key": v,
            "attributes": {
                "label": v,
                "size": round(size, 2),
                "color": hex_color(book_type, betweenness_norm),
                "bookType": book_type,
                "degree": float(row["degree_centrality"]) if row is not None else 0,
                "eigenvector": float(row["eigenvector_centrality"]) if row is not None else 0,
                "betweenness": float(row["betweenness_centrality"]) if row is not None else 0,
                "x": random.uniform(-1, 1),
                "y": random.uniform(-1, 1),
            },
        })

    edges = [{"source": r["source"], "target": r["target"]} for _, r in edges_df.iterrows()]

    return {"nodes": nodes, "edges": edges}


def main():
    print("Carregando dados...")
    edges_df = pd.read_csv(CSV_EDGES)
    metrics_df = pd.read_csv(CSV_METRICS)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Gerando graph_full.json (pode demorar)...")
    full_graph = build_graph_data(edges_df, metrics_df)
    with open(OUTPUT_DIR / "graph_full.json", "w", encoding="utf-8") as f:
        json.dump(full_graph, f, ensure_ascii=False)
    print(f"  {len(full_graph['nodes'])} nós, {len(full_graph['edges'])} arestas")

    print("Gerando graph_top500.json...")
    top500_graph = build_graph_data(edges_df, metrics_df, top_n=500)
    with open(OUTPUT_DIR / "graph_top500.json", "w", encoding="utf-8") as f:
        json.dump(top500_graph, f, ensure_ascii=False)
    print(f"  {len(top500_graph['nodes'])} nós, {len(top500_graph['edges'])} arestas")

    print("Gerando verses_autocomplete.json...")
    verses = sorted(metrics_df["versiculo"].tolist())
    with open(OUTPUT_DIR / "verses_autocomplete.json", "w", encoding="utf-8") as f:
        json.dump(verses, f, ensure_ascii=False)
    print(f"  {len(verses)} versículos")

    print("\nConcluído.")


if __name__ == "__main__":
    main()

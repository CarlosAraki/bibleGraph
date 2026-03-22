#!/usr/bin/env python3
"""
Análise topológica da rede de referências cruzadas da Bíblia.
Calcula métricas de centralidade e gera visualização com destaque para os hubs principais.

Otimizações aplicadas:
- Betweenness: amostragem com k=1000 para estimativa (evita O(n³) exato)
- Eigenvector: fallback para PageRank se não convergir
- Visualização: subgrafo dos top 300 nós mais centrais (grafo completo = 340k arestas = impraticável)
"""

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
CSV_ENTRADA = SCRIPT_DIR / "referencias_nvi_cytoscape.csv"
CSV_METRICAS = SCRIPT_DIR / "metricas_topologicas_biblia.csv"
IMG_SAIDA = SCRIPT_DIR / "grafo_referencias_biblia.png"

# Parâmetro de amostragem para Betweenness (k nós amostrados = O(n²) em vez de O(n³))
K_BETWEENNESS = 1000

# Subgrafo para visualização (top N nós por score combinado)
TOP_NOS_VISUALIZACAO = 300

# DPI para imagem de alta resolução
DPI = 300


def carregar_grafo(caminho: Path) -> nx.DiGraph:
    """Carrega o CSV e constrói o grafo direcionado."""
    df = pd.read_csv(caminho)
    G = nx.from_pandas_edgelist(df, source="source", target="target", create_using=nx.DiGraph())
    return G


def calcular_metricas(G: nx.DiGraph) -> pd.DataFrame:
    """
    Calcula Degree, Eigenvector/PageRank e Betweenness (aproximado).
    Retorna DataFrame com todos os nós e suas métricas.
    """
    print("Calculando Degree Centrality...")
    degree = nx.degree_centrality(G)

    print("Calculando Eigenvector Centrality (fallback: PageRank)...")
    try:
        eigenvector = nx.eigenvector_centrality(G, max_iter=500, tol=1e-6)
    except (nx.PowerIterationFailedConvergence, nx.NetworkXError):
        print("  -> Eigenvector não convergiu. Usando PageRank.")
        eigenvector = nx.pagerank(G, max_iter=100)

    print(f"Calculando Betweenness Centrality (amostra k={K_BETWEENNESS})...")
    betweenness = nx.betweenness_centrality(G, k=K_BETWEENNESS, seed=42)

    # Normalizar para [0, 1] para facilitar visualização
    def norm(d: dict) -> dict:
        mx = max(d.values()) if d else 1
        return {k: v / mx for k, v in d.items()} if mx > 0 else d

    df = pd.DataFrame({
        "versiculo": list(G.nodes()),
        "degree_centrality": [degree.get(n, 0) for n in G.nodes()],
        "eigenvector_centrality": [eigenvector.get(n, 0) for n in G.nodes()],
        "betweenness_centrality": [betweenness.get(n, 0) for n in G.nodes()],
    })

    df["degree_norm"] = norm(degree)
    df["eigenvector_norm"] = norm(eigenvector)
    df["betweenness_norm"] = norm(betweenness)

    return df


def score_combinado(df: pd.DataFrame) -> pd.Series:
    """Score para ordenação: média ponderada das métricas normalizadas."""
    return (
        df["degree_norm"] * 0.3
        + df["eigenvector_norm"] * 0.4
        + df["betweenness_norm"] * 0.3
    )


def exportar_metricas(df: pd.DataFrame) -> None:
    """Salva métricas em CSV ordenado."""
    df_sorted = df.sort_values("eigenvector_centrality", ascending=False).reset_index(drop=True)
    cols_export = ["versiculo", "degree_centrality", "eigenvector_centrality", "betweenness_centrality"]
    df_sorted[cols_export].to_csv(CSV_METRICAS, index=False, encoding="utf-8")
    print(f"\nMétricas exportadas: {CSV_METRICAS}")


def imprimir_top10(df: pd.DataFrame) -> None:
    """Exibe Top 10 versículos mais centrais no terminal."""
    df_score = df.copy()
    df_score["score"] = score_combinado(df)
    top10 = df_score.nlargest(10, "score")

    print("\n" + "=" * 80)
    print("TOP 10 VERSÍCULOS MAIS CENTRAIS (referências cruzadas)")
    print("=" * 80)

    for i, row in enumerate(top10.itertuples(), 1):
        print(f"\n  {i:2}. {row.versiculo}")
        print(f"      Degree:      {row.degree_centrality:.6f}")
        print(f"      Eigenvector: {row.eigenvector_centrality:.6f}")
        print(f"      Betweenness: {row.betweenness_centrality:.6f}")

    print("\n" + "=" * 80)


def gerar_visualizacao(G: nx.DiGraph, df: pd.DataFrame) -> None:
    """
    Gera visualização do subgrafo dos nós mais centrais.
    Tamanho = Eigenvector | Cor = Betweenness | Labels = Top 10.
    """
    df_score = df.copy()
    df_score["score"] = score_combinado(df)
    top_nos = set(df_score.nlargest(TOP_NOS_VISUALIZACAO, "score")["versiculo"].tolist())

    # Subgrafo: nós top + arestas entre eles
    H = G.subgraph(top_nos).copy()

    # Converter para não-direcionado para layout (menos arestas duplicadas)
    H_undirected = H.to_undirected()

    print(f"\nGerando layout para subgrafo ({H.number_of_nodes()} nós, {H.number_of_edges()} arestas)...")
    pos = nx.spring_layout(H_undirected, k=1.5, iterations=80, seed=42)

    # Atributos para plot
    metricas = df.set_index("versiculo")
    node_sizes = [
        (metricas.loc[n, "eigenvector_norm"] * 800 + 50) if n in metricas.index else 50
        for n in H.nodes()
    ]
    node_colors = [
        metricas.loc[n, "betweenness_norm"] if n in metricas.index else 0
        for n in H.nodes()
    ]

    top10_versiculos = set(
        df_score.nlargest(10, "score")["versiculo"].tolist()
    )

    fig, ax = plt.subplots(figsize=(16, 12), facecolor="#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    # Desenhar arestas (mais finas e translúcidas)
    nx.draw_networkx_edges(H, pos, alpha=0.15, edge_color="#4a5568", arrows=False, ax=ax)

    # Colormap para Betweenness (viridis = amarelo = alto betweenness)
    cmap = plt.cm.plasma
    nodes = nx.draw_networkx_nodes(
        H, pos, node_size=node_sizes, node_color=node_colors,
        cmap=cmap, alpha=0.9, ax=ax
    )

    # Labels apenas dos Top 10
    labels_top10 = {n: n for n in H.nodes() if n in top10_versiculos}
    nx.draw_networkx_labels(
        H, pos, labels=labels_top10, font_size=9, font_color="white",
        font_weight="bold", ax=ax,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#2d3748", edgecolor="#4a9eff", alpha=0.9)
    )

    # Colorbar para Betweenness
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=1))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label("Betweenness Centrality (normalizado)", color="white", fontsize=10)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")

    ax.set_title(
        "Rede de Referências Cruzadas da Bíblia (NVI)\n"
        "Tamanho = Eigenvector | Cor = Betweenness | Top 300 nós",
        fontsize=14, color="white", pad=20
    )
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(
        IMG_SAIDA, dpi=DPI, bbox_inches="tight",
        facecolor="#1a1a2e", edgecolor="none"
    )
    plt.close()

    print(f"Visualização salva: {IMG_SAIDA}")


def main():
    print("=" * 60)
    print("Análise Topológica - Referências Cruzadas da Bíblia")
    print("=" * 60)

    if not CSV_ENTRADA.exists():
        print(f"Erro: {CSV_ENTRADA} não encontrado.")
        print("Execute primeiro: python gerar_referencias_biblicas.py")
        return

    print(f"\nCarregando grafo de {CSV_ENTRADA}...")
    G = carregar_grafo(CSV_ENTRADA)
    print(f"  Nós: {G.number_of_nodes():,} | Arestas: {G.number_of_edges():,}")

    df = calcular_metricas(G)
    exportar_metricas(df)
    imprimir_top10(df)
    gerar_visualizacao(G, df)

    print("\nConcluído!")


if __name__ == "__main__":
    main()

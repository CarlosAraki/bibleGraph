#!/usr/bin/env python3
"""
Script para gerar CSV de referências cruzadas da Bíblia (padrão NVI)
a partir do dataset OpenBible.info para uso no Cytoscape.

Fonte: https://www.openbible.info/labs/cross-references/
Dataset: https://a.openbible.info/data/cross-references.zip
"""

import csv
import re
import sys
import urllib.request
import zipfile
from io import BytesIO, TextIOWrapper
from pathlib import Path

# =============================================================================
# MAPEAMENTO: Abreviações OpenBible (inglês) -> Nomes completos NVI (português)
# =============================================================================
LIVROS_EN_PT = {
    # Antigo Testamento
    "Gen": "Gênesis",
    "Exod": "Êxodo",
    "Lev": "Levítico",
    "Num": "Números",
    "Deut": "Deuteronômio",
    "Josh": "Josué",
    "Judg": "Juízes",
    "Ruth": "Rute",
    "1Sam": "1 Samuel",
    "2Sam": "2 Samuel",
    "1Kgs": "1 Reis",
    "2Kgs": "2 Reis",
    "1Chr": "1 Crônicas",
    "2Chr": "2 Crônicas",
    "Ezra": "Esdras",
    "Neh": "Neemias",
    "Esth": "Ester",
    "Job": "Jó",
    "Ps": "Salmos",
    "Prov": "Provérbios",
    "Eccl": "Eclesiastes",
    "Song": "Cânticos",
    "Isa": "Isaías",
    "Jer": "Jeremias",
    "Lam": "Lamentações",
    "Ezek": "Ezequiel",
    "Dan": "Daniel",
    "Hos": "Oseias",
    "Joel": "Joel",
    "Amos": "Amós",
    "Obad": "Obadias",
    "Jonah": "Jonas",
    "Mic": "Miquéias",
    "Nah": "Naum",
    "Hab": "Habacuque",
    "Zeph": "Sofonias",
    "Hag": "Ageu",
    "Zech": "Zacarias",
    "Mal": "Malaquias",
    # Novo Testamento
    "Matt": "Mateus",
    "Mark": "Marcos",
    "Luke": "Lucas",
    "John": "João",
    "Acts": "Atos",
    "Rom": "Romanos",
    "1Cor": "1 Coríntios",
    "2Cor": "2 Coríntios",
    "Gal": "Gálatas",
    "Eph": "Efésios",
    "Phil": "Filipenses",
    "Col": "Colossenses",
    "1Thess": "1 Tessalonicenses",
    "2Thess": "2 Tessalonicenses",
    "1Tim": "1 Timóteo",
    "2Tim": "2 Timóteo",
    "Titus": "Tito",
    "Phlm": "Filemom",
    "Heb": "Hebreus",
    "Jas": "Tiago",
    "1Pet": "1 Pedro",
    "2Pet": "2 Pedro",
    "1John": "1 João",
    "2John": "2 João",
    "3John": "3 João",
    "Jude": "Judas",
    "Rev": "Apocalipse",
}

# Regex para parsing: Livro.Capítulo.Versículo ou Livro.Capítulo.Versículo-Livro.Capítulo.Versículo
REF_PATTERN = re.compile(r"^([0-9]?[A-Za-z]+)\.(\d+)\.(\d+)(?:-([0-9]?[A-Za-z]+)\.(\d+)\.(\d+))?$")


def parse_referencia(ref: str) -> tuple[str, str] | None:
    """
    Converte referência do formato OpenBible (ex: Gen.1.1 ou John.1.1-John.1.3)
    para formato NVI (ex: Gênesis 1:1).

    Para ranges (ex: John.1.1-John.1.3), retorna apenas o primeiro versículo (João 1:1).
    Retorna None se a abreviação não estiver no dicionário.
    """
    match = REF_PATTERN.match(ref.strip())
    if not match:
        return None

    book_abbrev, chapter, verse = match.group(1), match.group(2), match.group(3)
    book_pt = LIVROS_EN_PT.get(book_abbrev)
    if not book_pt:
        return None

    return f"{book_pt} {chapter}:{verse}"


def baixar_dataset(url: str = "https://a.openbible.info/data/cross-references.zip") -> bytes:
    """Baixa o dataset ZIP do OpenBible."""
    print("Baixando dataset do OpenBible.info...")
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def processar_referencias(arquivo_txt: TextIOWrapper) -> tuple[list[tuple[str, str]], int]:
    """
    Processa o arquivo TXT e retorna lista de (source, target) e contagem de erros.
    """
    reader = csv.reader(arquivo_txt, delimiter="\t")
    arestas: list[tuple[str, str]] = []
    erros = 0

    for i, row in enumerate(reader):
        if i == 0:
            # Pular cabeçalho
            continue
        if len(row) < 2:
            erros += 1
            continue

        source_raw, target_raw = row[0], row[1]

        # Para targets com range (ex: John.1.1-John.1.3), usar apenas a primeira parte
        if "-" in target_raw and "." in target_raw:
            target_raw = target_raw.split("-")[0]

        source = parse_referencia(source_raw)
        target = parse_referencia(target_raw)

        if source is None or target is None:
            erros += 1
            continue

        arestas.append((source, target))

    return arestas, erros


def main():
    script_dir = Path(__file__).parent.resolve()
    output_path = script_dir / "referencias_nvi_cytoscape.csv"

    print("=" * 60)
    print("Gerador de Referências Cruzadas Bíblicas (OpenBible -> NVI)")
    print("=" * 60)

    try:
        zip_data = baixar_dataset()
    except Exception as e:
        print(f"Erro ao baixar dataset: {e}", file=sys.stderr)
        sys.exit(1)

    print("Extraindo e processando referências...")

    with zipfile.ZipFile(BytesIO(zip_data), "r") as zf:
        with zf.open("cross_references.txt") as f:
            with TextIOWrapper(f, encoding="utf-8", errors="replace") as txt:
                arestas, erros = processar_referencias(txt)

    # Remover duplicatas (source, target) mantendo a ordem
    arestas_unicas: list[tuple[str, str]] = []
    visto = set()
    for s, t in arestas:
        chave = (s, t)
        if chave not in visto:
            visto.add(chave)
            arestas_unicas.append(chave)

    print(f"\nEscrevendo {len(arestas_unicas):,} arestas em {output_path}")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["source", "target"])
        writer.writerows(arestas_unicas)

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"  Referências processadas com sucesso: {len(arestas_unicas):,}")
    if erros > 0:
        print(f"  Linhas ignoradas (abreviação desconhecida ou formato inválido): {erros:,}")
    print(f"  Arquivo gerado: {output_path}")
    print("=" * 60)
    print("\nPronto para importar no Cytoscape!")
    print("Dica: use importação como 'Directed' e layout Prefuse Force Directed ou yFiles Organic.")


if __name__ == "__main__":
    main()

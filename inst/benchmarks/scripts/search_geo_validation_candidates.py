from __future__ import annotations

import csv
import os
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_CSV = ROOT / "GEO_EXPANDED_SEARCH_CANDIDATES.csv"
OUT_MD = ROOT / "GEO_EXPANDED_SEARCH_CANDIDATES.md"
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
MAX_FILELISTS = int(os.environ.get("MAX_FILELISTS", "180"))

SEARCH_TERMS = [
    "MERSCOPE",
    "MERFISH",
    "Xenium",
    "CosMx",
    "seqFISH",
    "spatial transcriptomics cell type",
    "spatial transcriptomics h5ad cell type",
    "spatial transcriptomics cell annotation",
    "cell by gene coordinates cell type",
]

EXPRESSION_RE = re.compile(
    r"(h5ad|cell[_-]?by[_-]?gene|count|counts|matrix|mtx|feature[_-]?bc[_-]?matrix|expression|expr)",
    re.IGNORECASE,
)
COORD_RE = re.compile(
    r"(coordinate|coordinates|centroid|cell[_-]?metadata|metadata|spatial|location|cellpose|segmentation)",
    re.IGNORECASE,
)
LABEL_RE = re.compile(
    r"(cell[_-]?type|celltype|celltypes|annotation|annotations|cluster|clusters|label|labels|subclass|class)",
    re.IGNORECASE,
)
PLATFORM_RE = re.compile(r"(merscope|merfish|xenium|cosmx|seqfish|spatial)", re.IGNORECASE)
IMMUNE_RECEPTOR_RE = re.compile(
    r"(filtered[_-]?contig|all[_-]?contig|contig[_-]?annotations?|consensus[_-]?annotations?|"
    r"vdj[_-]?[bt]?|bcr|tcr|clonotype|airr)",
    re.IGNORECASE,
)
IMAGE_LABEL_RE = re.compile(
    r"(celllabels|compartmentlabels|mask|segmentation|hires[_-]?image|lowres[_-]?image|"
    r"\.(png|jpe?g|tiff?|svs)(\.gz)?$)",
    re.IGNORECASE,
)


def usable_label_file(name: str) -> bool:
    return bool(LABEL_RE.search(name)) and not IMMUNE_RECEPTOR_RE.search(name) and not IMAGE_LABEL_RE.search(name)


def usable_coordinate_file(name: str) -> bool:
    return bool(COORD_RE.search(name)) and not IMAGE_LABEL_RE.search(name)


def fetch_json(url: str, timeout: int = 40) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as handle:
        return json.load(handle)


def esearch(term: str) -> list[str]:
    url = NCBI_BASE + "esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "gds", "term": term, "retmax": "300", "retmode": "json"}
    )
    data = fetch_json(url)
    return data["esearchresult"].get("idlist", [])


def esummary(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    url = NCBI_BASE + "esummary.fcgi?" + urllib.parse.urlencode(
        {"db": "gds", "id": ",".join(ids), "retmode": "json"}
    )
    data = fetch_json(url)
    result = data["result"]
    return {uid: result[uid] for uid in result.get("uids", [])}


def ftp_to_filelist(ftplink: str) -> str | None:
    if not ftplink:
        return None
    base = ftplink.replace("ftp://ftp.ncbi.nlm.nih.gov", "https://ftp.ncbi.nlm.nih.gov").rstrip("/")
    return f"{base}/suppl/filelist.txt"


def parse_filelist(text: str) -> tuple[int, int, list[str]]:
    rows = []
    total_size = 0
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    for row in reader:
        name = row.get("Name", "")
        rows.append(name)
        try:
            total_size += int(row.get("Size", "0") or 0)
        except ValueError:
            pass
    return len(rows), total_size, rows


def get_filelist(item: dict) -> dict:
    url = ftp_to_filelist(item.get("ftplink", ""))
    if not url:
        return {"filelist_url": "", "file_count": 0, "total_supp_size": 0, "files": []}
    try:
        with urllib.request.urlopen(url, timeout=18) as handle:
            text = handle.read().decode("utf-8", errors="replace")
        file_count, total_size, files = parse_filelist(text)
        return {
            "filelist_url": url,
            "file_count": file_count,
            "total_supp_size": total_size,
            "files": files,
        }
    except Exception as exc:  # noqa: BLE001 - record screening failures.
        return {
            "filelist_url": url,
            "file_count": 0,
            "total_supp_size": 0,
            "files": [],
            "filelist_error": str(exc),
        }


def summarize_files(files: list[str]) -> tuple[str, str, str, str]:
    expr = [name for name in files if EXPRESSION_RE.search(name)]
    coord = [name for name in files if usable_coordinate_file(name)]
    label = [name for name in files if usable_label_file(name)]
    h5ad = [name for name in files if name.lower().endswith(".h5ad") or ".h5ad" in name.lower()]
    def join(names: list[str]) -> str:
        return "; ".join(names[:8])
    return join(expr), join(coord), join(label), join(h5ad)


def score_candidate(item: dict, files: list[str]) -> tuple[int, str]:
    expr_files, coord_files, label_files, h5ad_files = summarize_files(files)
    text = " ".join(
        [
            item.get("title", ""),
            item.get("summary", ""),
            item.get("suppfile", ""),
            " ".join(files[:80]),
        ]
    )
    score = 0
    reasons = []
    if PLATFORM_RE.search(text):
        score += 2
        reasons.append("spatial/platform term")
    if EXPRESSION_RE.search(text):
        score += 2
        reasons.append("expression-like files")
    if coord_files:
        score += 2
        reasons.append("coordinate/metadata-like files")
    if label_files:
        score += 2
        reasons.append("label/annotation-like files")
    if h5ad_files or re.search(r"h5ad", text, flags=re.IGNORECASE):
        score += 1
        reasons.append("h5ad")
    if item.get("entrytype") == "GSE":
        score += 1
    return score, "; ".join(reasons)


def preliminary_score(item: dict, terms: set[str]) -> int:
    text = " ".join([item.get("title", ""), item.get("summary", ""), item.get("suppfile", ""), " ".join(terms)])
    score = 0
    if PLATFORM_RE.search(text):
        score += 2
    if EXPRESSION_RE.search(text):
        score += 2
    if COORD_RE.search(text):
        score += 1
    if LABEL_RE.search(text):
        score += 1
    if re.search(r"(h5ad|csv|tsv|tar|h5|mtx|rds)", item.get("suppfile", ""), flags=re.IGNORECASE):
        score += 1
    return score


def main() -> None:
    accessions: dict[str, dict] = {}
    matched_terms: dict[str, set[str]] = {}
    for term in SEARCH_TERMS:
        ids = esearch(term)
        print(f"{term}: {len(ids)} ids", flush=True)
        for start in range(0, len(ids), 50):
            chunk = ids[start : start + 50]
            for item in esummary(chunk).values():
                if item.get("entrytype") != "GSE":
                    continue
                acc = item.get("accession", "")
                if not acc.startswith("GSE"):
                    continue
                accessions[acc] = item
                matched_terms.setdefault(acc, set()).add(term)
            time.sleep(0.12)

    print(f"GSE candidates before file screening: {len(accessions)}", flush=True)
    ranked_for_filelist = sorted(
        accessions,
        key=lambda acc: (-preliminary_score(accessions[acc], matched_terms.get(acc, set())), acc),
    )
    ranked_for_filelist = [
        acc
        for acc in ranked_for_filelist
        if preliminary_score(accessions[acc], matched_terms.get(acc, set())) >= 3
    ][:MAX_FILELISTS]
    print(f"fetching supplement file lists for: {len(ranked_for_filelist)}", flush=True)
    file_info: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(get_filelist, accessions[acc]): acc for acc in ranked_for_filelist}
        for idx, future in enumerate(as_completed(futures), start=1):
            acc = futures[future]
            file_info[acc] = future.result()
            if idx % 50 == 0:
                print(f"screened file lists: {idx}/{len(futures)}", flush=True)

    rows = []
    for acc, item in accessions.items():
        files = file_info.get(acc, {}).get("files", [])
        expr_files, coord_files, label_files, h5ad_files = summarize_files(files)
        score, reason = score_candidate(item, files)
        rows.append(
            {
                "accession": acc,
                "score": score,
                "matched_terms": "; ".join(sorted(matched_terms.get(acc, []))),
                "title": item.get("title", ""),
                "pdat": item.get("pdat", ""),
                "n_samples": item.get("n_samples", ""),
                "taxon": item.get("taxon", ""),
                "suppfile": item.get("suppfile", ""),
                "geo_url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={acc}",
                "filelist_url": file_info.get(acc, {}).get("filelist_url", ""),
                "file_count": file_info.get(acc, {}).get("file_count", 0),
                "total_supp_size_gb": round(file_info.get(acc, {}).get("total_supp_size", 0) / 1e9, 3),
                "h5ad_files": h5ad_files,
                "expression_evidence": expr_files,
                "coordinate_evidence": coord_files,
                "label_evidence": label_files,
                "screening_reason": reason,
            }
        )

    rows.sort(key=lambda row: (-int(row["score"]), row["accession"]))
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    top = [row for row in rows if int(row["score"]) >= 7][:40]
    lines = [
        "# Expanded GEO Validation Candidate Search",
        "",
        "Automated search over NCBI GEO DataSets using MERSCOPE, MERFISH, Xenium, CosMx, seqFISH, and spatial-transcriptomics annotation terms.",
        "",
        f"- total GSE candidates screened: {len(rows)}",
        f"- high-priority candidates with score >= 7: {sum(int(row['score']) >= 7 for row in rows)}",
        "",
        "## Top Candidates",
        "",
        "| accession | score | date | samples | supp | size GB | why | title |",
        "|---|---:|---|---:|---|---:|---|---|",
    ]
    for row in top:
        title = row["title"].replace("|", "/")[:100]
        lines.append(
            f"| {row['accession']} | {row['score']} | {row['pdat']} | {row['n_samples']} | "
            f"{row['suppfile']} | {row['total_supp_size_gb']} | {row['screening_reason']} | {title} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()

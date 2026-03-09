from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


LATERALITY_PATTERN = re.compile(r"\b(left|right|bilateral)\b", re.IGNORECASE)
VISUAL_PATTERN = re.compile(r"\bLC[_A-Za-z0-9]*\b|\bloom|\bvision|\bvisual\b", re.IGNORECASE)
MECH_PATTERN = re.compile(r"\bJON[_A-Za-z0-9]*\b|\bJO_[A-Za-z0-9_]*\b|\ball_JOs\b|\bmechanosensory\b", re.IGNORECASE)
GUSTATORY_PATTERN = re.compile(r"\bsugar\b|\bwater\b|\bgust", re.IGNORECASE)
OLFACTORY_PATTERN = re.compile(r"\bOr\d+[A-Za-z0-9_]*\b|\bolfac", re.IGNORECASE)
ASSIGNMENT_PATTERN = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*=")


def classify_categories(text: str) -> list[str]:
    categories: list[str] = []
    if VISUAL_PATTERN.search(text):
        categories.append("visual")
    if MECH_PATTERN.search(text):
        categories.append("mechanosensory")
    if GUSTATORY_PATTERN.search(text):
        categories.append("gustatory")
    if OLFACTORY_PATTERN.search(text):
        categories.append("olfactory")
    return categories


def scan_notebook(path: Path) -> list[dict[str, object]]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    hits: list[dict[str, object]] = []
    previous_markdown = ""
    for cell_index, cell in enumerate(notebook.get("cells", [])):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            previous_markdown = source
            continue
        if cell.get("cell_type") != "code":
            continue
        context = f"{previous_markdown}\n{source}"
        context_categories = classify_categories(context)
        if not context_categories:
            continue
        for line_number, line in enumerate(source.splitlines(), start=1):
            categories = classify_categories(f"{previous_markdown}\n{line}")
            if not categories:
                continue
            assignment_match = ASSIGNMENT_PATTERN.match(line)
            is_comment = line.lstrip().startswith("#")
            laterality_terms = sorted({term.lower() for term in LATERALITY_PATTERN.findall(f"{previous_markdown}\n{line}")})
            if assignment_match is None and not (is_comment and laterality_terms):
                continue
            hits.append(
                {
                    "path": str(path),
                    "cell_index": cell_index,
                    "line_number_in_cell": line_number,
                    "categories": categories,
                    "variable_name": assignment_match.group(1) if assignment_match else None,
                    "laterality_terms": laterality_terms,
                    "line": line.strip(),
                    "markdown_context": previous_markdown.strip(),
                }
            )
    return hits


def summarize(hits: list[dict[str, object]]) -> dict[str, object]:
    def select(category: str, require_laterality: bool | None) -> list[dict[str, object]]:
        selected = []
        for hit in hits:
            if category not in hit["categories"]:
                continue
            has_laterality = bool(hit["laterality_terms"])
            if require_laterality is True and not has_laterality:
                continue
            if require_laterality is False and has_laterality:
                continue
            selected.append(hit)
        return selected

    return {
        "visual_lateralized_hits": select("visual", True),
        "visual_non_lateralized_hits": select("visual", False),
        "mechanosensory_lateralized_hits": select("mechanosensory", True),
        "mechanosensory_non_lateralized_hits": select("mechanosensory", False),
        "gustatory_lateralized_hits": select("gustatory", True),
        "olfactory_lateralized_hits": select("olfactory", True),
        "notes": [
            "This search only reflects the checked public artifacts in the local workspace.",
            "A hit is marked lateralized when the code line or the immediately preceding markdown context contains 'left', 'right', or 'bilateral'.",
            "Non-lateralized visual and mechanosensory hits are useful for showing what public anchors exist but are not explicitly side-specific.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Search checked public artifacts for lateralized sensory anchors.")
    parser.add_argument(
        "--root",
        default="external/fly-brain/code/paper-phil-drosophila",
        help="Directory containing the checked public notebook artifacts.",
    )
    parser.add_argument(
        "--output",
        default="outputs/metrics/lateralized_public_anchors.json",
        help="Path to write the search results JSON.",
    )
    args = parser.parse_args()

    root = Path(args.root)
    output = Path(args.output)
    hits: list[dict[str, object]] = []
    for notebook_path in sorted(root.rglob("*.ipynb")):
        hits.extend(scan_notebook(notebook_path))
    summary = summarize(hits)
    summary["scanned_root"] = str(root)
    summary["num_hits"] = len(hits)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()

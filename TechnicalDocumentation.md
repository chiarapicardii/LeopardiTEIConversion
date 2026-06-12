# Technical Documentation: From WikiLeopardi to XML/TEI
This document serves as a detailed report of the main technical choices, problems encountered and function implemented in the conversion script (`teiconversion.py`).

## Pipeline Logic
The table below maps each programming node to its specific technical implementation and its relative philological objective within the TEI ecosystem.

| Programming Node | Core Method / Function | Algorithmic Core (Regex / Logic) | Philological Solution & TEI Target |
| :--- | :--- | :--- | :--- |
| **1. Witness Resolution** | `run_all()` | Preliminary global scan using `set()` and mapping via `canto_witnesses_set`. | Solves missing explicit acronyms in individual pages by applying a contextual fallback list. |
| **2. Header Generation** | `generate_tei_header()` <br> `build_witness_list()` | String parsing through `witness_pattern` and automated injection. | Generates a valid `<teiHeader>` containing the full `<listWit>` schema based on declared witnesses. |
| **3. Facsimile Anchoring** | `insert_pb()` <br> `build_facsimile()` | Dictionary mapping (`facs_map`) extracting page numbers from `facsimile_pattern`. | Links page breaks (`<pb facs="#ID"/>`) to digital facsimiles, enabling split-screen rendering in EVT. |
| **4. Apparatus Parsing** | `replace_wit()` <br> `avoid_repetition_appatatus()` | Three conditional replacement rules managed via regex syntax patterns. | Maps wikilinks into `<app>`, `<lem>`, and `<rdg>` elements, skipping redundant text variants. |
| **5. Prose Segmentation** | `encode_div()` *(Prose branch)* | Detection via `json_key.lower()` and paragraph splits through `\n\n`. | Identifies notes or letters, wraps them in `<div type="note\|letter">`, and maps paragraphs to `<p>`. |
| **6. Metric Encoding** | `encode_div()` *(Poem branch)* <br> `encode_verses()` | Line-by-line normalization and isolation via `isolate_verse_num()`. | Identifies poetic structures, wraps text in line groups (`<lg>`), and numbers each structural verse line (`<l n="N">`). |

---

## 🛠️ Detailed Node Analysis & Code Implementation

### Node 1: Global Pre-scanning & Witness Inheritance
The script addresses the structural lack of explicit witness declarations for individual text variants by scanning the entire JSON file before initiating the document generation.
```python
# Extracting witnesses dynamically to build a global fallback system
for key, text in data.items():
    canto_match = re.search(r"CANTO\s+\w+", key)
    if not canto_match: continue
    canto = canto_match.group(0)
    ...
    if page_witnesses:
        canto_witnesses_set[canto].update(page_witnesses)

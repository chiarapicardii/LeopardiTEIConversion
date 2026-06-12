# Technical Documentation: From WikiLeopardi to XML/TEI

This document details the main technical choices, problems encountered, and functions implemented in `teiconversion.py`.

---

## Pipeline Overview

| # | Node | Core Function | TEI Target |
|:--|:-----|:-------------|:-----------|
| 1 | Global Witness Pre-scanning | `run_all()` | `<listWit>` fallback across corpus |
| 2 | TEI Header Generation | `generate_tei_header()` | Valid `<teiHeader>` per file |
| 3 | Title Apparatus | `extract_structured_title()` | `<head><app>…</app></head>` |
| 4 | Critical Apparatus Parsing | `replace_wit()` | `<app><lem><rdg>` elements |
| 5 | Facsimile Anchoring | `insert_pb()`, `build_facsimile()` | `<pb facs="#id"/>` + `<facsimile>` |
| 6 | Prose / Poetry Branching | `encode_div()` | `<div type="poem|note|letter">` |
| 7 | Metric Encoding | `encode_verses()` | `<l n="N">` within `<lg>` |

---

## Node 1 — Global Witness Pre-scanning

**Problem:** WikiLeopardi declares witnesses only on the first page of each canto. Subsequent pages carry no explicit witness list, which would leave most `<rdg>` elements without a valid `wit` attribute.

**Solution:** before any conversion begins, `run_all()` performs a full-corpus scan, building a per-canto witness dictionary and a global fallback list.

```python
canto_witnesses_set = {}
global_witnesses = set()

for key, text in data.items():
    canto_match = re.search(r"CANTO\s+\w+", key)
    if not canto_match:
        continue
    canto = canto_match.group(0)

    header_part = text.split(poem_tag, 1)[0] if poem_tag in text else text
    page_witnesses = extract_witnesses(header_part)

    for wit in page_witnesses:
        global_witnesses.add(wit)

    if canto not in canto_witnesses_set:
        canto_witnesses_set[canto] = set()
    if page_witnesses:
        canto_witnesses_set[canto].update(page_witnesses)
```

If a canto page declares no witnesses, the script falls back to the full global witness set:

```python
if not current_witnesses or current_witnesses == [main_witness]:
    body_witnesses = body_fallback_witnesses
    head_witnesses = sorted(list(set(head_fallback_witnesses + [main_witness])))
```

> **Philological note:** variants without explicit witness attribution are assigned to the full set of declared witnesses — a documented limitation requiring manual review for full philological reliability. See [Limitations](#limitations).

---

## Node 2 — TEI Header Generation

**Solution:** `generate_tei_header()` assembles a complete `<teiHeader>` for every output file, injecting the witness list resolved in Node 1 and hardcoding the encoding method.

```python
def generate_tei_header(title, witnesses, encoder_name="Chiara Picardi", ...):
    list_wit = build_witness_list(witnesses)
    header = f"""  <teiHeader>
      <fileDesc>
        <titleStmt>
          <title>{title}</title>
          <author>Giacomo Leopardi</author>
          <respStmt>
            <resp>Encoded by</resp>
            <persName>{encoder_name}</persName>
          </respStmt>
        </titleStmt>
        ...
        <sourceDesc>
          <bibl>{source_bibl}</bibl>
          {list_wit}
        </sourceDesc>
      </fileDesc>
      <encodingDesc>
        <variantEncoding method="parallel-segmentation" location="internal"/>
      </encodingDesc>
    </teiHeader>"""
```

The `variantEncoding` declaration is essential for EVT to render the critical apparatus correctly.

---

## Node 3 — Title Apparatus

**Problem:** titles themselves vary across witnesses in WikiLeopardi. A naive extraction would discard this information.

**Solution:** `extract_structured_title()` uses `re.findall()` to collect all `[[Titolo:edition|text]]` patterns. The first match becomes the `<lem>`, subsequent ones become `<rdg>` elements.

```python
titles = re.findall(r"\[\[Titolo:([^|\]]+)\|([^\]]+)\]\]", wikitext, re.DOTALL)

base_edition, base_text = titles[0]

# If only one title, no apparatus needed
if len(titles) == 1:
    return f'<head>{base_text}</head>'

# Otherwise build the full apparatus
app_editions = []
for edition, text in titles[1:]:
    app_editions.append(f'<rdg wit="#{edition}">{text}</rdg>')

return f'<head><app><lem wit="#{base_edition}">{base_text}</lem>{"".join(app_editions)}</app></head>'
```

**Fallback:** when the extracted title is a lone Roman numeral (e.g. `IV`) — a recurring WikiLeopardi formatting issue — the function falls back to the JSON key.

```python
if not re.fullmatch(r'[IVXLCDM]+', clean_title):
    return clean_title
# else: use clean_fallback from JSON key
```

---

## Node 4 — Critical Apparatus Parsing

**Problem:** WikiLeopardi encodes variants in three distinct syntactic patterns that must all be mapped to TEI `<app>` elements.

**Solution:** `replace_wit()` applies three sequential regex substitutions.

### Case 1 — Explicit witness: `[[Sigla:Variant|Lemma]]`

```python
text = re.sub(
    r"\[\[([A-Z]\d{2}):([^\]|]+)\|([^\]]+)\]\]",
    lambda m: avoid_repetition_apparatus(
        clean(m.group(3)),  # lemma
        clean(m.group(2)),  # reading
        f"#{m.group(1)}",   # witness sigla
    ),
    text, flags=re.DOTALL
)
```

### Case 2 — Pipe without sigla: `[[Variant|Lemma]]`

When the variant contains a `<lb/>` line break, the break is removed and the reading is flattened to a single string. This is a deliberate technical compromise: EVT cannot render a `<rdg>` element that breaks across lines, and preserving the `<lb/>` would corrupt the apparatus structure.

```python
def pipe(match):
    lem = clean(match.group(2))
    rdg = clean(match.group(1))
    if "<lb/>" in rdg or "\n" in rdg:
        clean_rdg = rdg.replace("<lb/>", " ").replace("\n", " ")
        return (
            f'<app><lem wit="#{main_witness}">{lem}</lem>'
            f'<rdg wit="{secondary_wits_string}">{clean_rdg}</rdg></app>'
        )
    return avoid_repetition_apparatus(lem, rdg, secondary_wits_string)
```

### Case 3 — Plain link: `[[text]]`

```python
text = re.sub(
    r"\[\[([^\]|]+)\]\]",
    lambda m: avoid_repetition_apparatus(
        clean(m.group(1)),
        clean(m.group(1)),
        secondary_wits_string,
    ),
    text, flags=re.DOTALL
)
```

### Deduplication

```python
def avoid_repetition_apparatus(lem, rdg, wit):
    if lem == rdg:
        return lem  # no apparatus needed: identical readings
    return f'<app><lem wit="#{main_witness}">{lem}</lem><rdg wit="{wit}">{rdg}</rdg></app>'
```

---

## Node 5 — Facsimile Anchoring

**Problem:** `<pb>` elements and facsimile images need to be linked by page number, but the connection is implicit in the filename (`F31x747.JPG` → page 747).

**Solution:** `insert_pb()` builds a `facs_map` by extracting the trailing three-digit number from each filename, then injects the `facs` attribute into every `<pb>` element.

```python
facs_map = {}
for f in facs_files:
    xml_id = f["xml_id"]
    page_num_match = re.search(r'\d{3}$', xml_id)
    if page_num_match:
        key = str(int(page_num_match.group(0)))
        facs_map[key] = xml_id

def replacer(match):
    num = match.group(1)
    xml_id = facs_map.get(num)
    if xml_id:
        return f'<pb n="{num}" facs="#{xml_id}"/>'
    return f'<pb n="{num}"/>'
```

`build_facsimile()` then produces the corresponding `<facsimile>` block in the TEI header:

```xml
<facsimile>
  <surface xml:id="F31x747">
    <graphic url="./assets/img/F31x747.JPG"/>
  </surface>
</facsimile>
```

This binding enables EVT's split-screen view, pairing the edited text with the original 1831 Florentine print.

---

## Node 6 — Prose / Poetry Branching

**Problem:** the corpus contains not only poems but also authorial notes, letters, and annotations — each requiring a different TEI structure.

**Solution:** `encode_div()` determines `div_type` through keyword detection on the JSON key, with a heuristic fallback on the text content itself.

```python
jk_lower = json_key.lower()

if "lettera" in jk_lower:
    div_type = "letter"
elif "nota" in jk_lower or "note" in jk_lower or "annotazioni" in jk_lower:
    div_type = "note"
else:
    # Heuristic: if no numbered verse pattern is found, treat as prose
    if not re.search(r'^\s*\d+\s+[A-Za-zÀ-ÿ]', text, re.MULTILINE):
        div_type = "note"
    else:
        div_type = "poem"
```

Prose texts are wrapped in `<p>` elements; notes receive a `corresp` attribute linking them to their parent canto by `xml:id`:

```python
canto_id = make_safe_id(canto_clean)
corresp_attribute = f' corresp="#{canto_id}"'
# → <div type="note" xml:id="..." corresp="#canto_i">
```

Poetry is wrapped in `<div type="poem"><lg>…</lg></div>` by Node 7.

---

## Node 7 — Metric Encoding

**Problem:** WikiLeopardi stores verse numbers inline with the text; they must be separated and mapped to the TEI `n` attribute without corrupting adjacent apparatus elements.

**Solution:** `isolate_verse_num()` uses a negative-lookbehind regex to distinguish verse numbers from page references, footnote numbers, and attribute values:

```python
text = re.sub(
    r'(?<!p\.)(?<!p\.\s)(?<!n=")(?<!facs=")(?<!wit=")\b(\d{1,3})\b\s+(?=[A-Za-zÀ-ÿ\[\('""<])',
    r'\n\1 ',
    text
)
```

`encode_verses()` then processes each line:

```python
match = re.match(r'^\s*([1-9][0-9]{0,2})?\s*(.*)', stripped_line)
num = match.group(1)
verse = match.group(2).strip()

n_attribute = f' n="{num}"' if num else ''
formatted_lines.append(f'        <l{n_attribute}>{verse}</l>')
```

Metrically indented lines preserve `rend="indent"` as a TEI attribute.

---

## Limitations

WikiLeopardi's syntax does not systematically require specifying the witness associated with each variant. As a result, a substantial portion of the apparatus lacks explicit witness attribution. The script addresses this by assigning such variants to the full set of declared witnesses; however, **a manual review remains necessary for full philological reliability**.

---

*Scripts and data are openly available under CC BY 4.0.*  
*Encoded by Chiara Picardi — University of Bologna, 2025–26.*

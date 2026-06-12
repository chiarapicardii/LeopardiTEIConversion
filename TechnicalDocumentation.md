# Technical Documentation: From WikiLeopardi to XML/TEI

This document details the main technical choices, problems encountered, and functions implemented in `teiconversion.py`.

---

## Pipeline Overview

|  | Issue | Function | TEI resolution |
|:--|:-----|:-------------|:-----------|
| 1 | Global witness dictionary | `run_all()` | `<listWit>` fallback across corpus |
| 2 | Title apparatus | `extract_structured_title()` | `<head><app>…</app></head>` |
| 3 | Critical Apparatus handling | `replace_wit()` | `<app><lem><rdg>` elements |
| 4 | Prose and Poetry division | `encode_div()` | `<div type="poem,note,letter">` |
| 5 | Metric Encoding | `encode_verses()` | `<l n="N">` within `<lg>` |

---

## Issue 1: Global witness dictionary

**Problem:** WikiLeopardi declares witnesses only on the first page of each canto, the pages following have no **explicit witness** list.

**Solution:** before any conversion begins, `run_all()` performs a full-corpus scan, building a witness dictionary (for the whole canto) and a global fallback list.

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

> **Philological note:** variants without explicit witness attribution are assigned to whole dictionary of declared witnesses, which means the files **need** manual review for full philological reliability. See [Limitation]paragraph in the project documentation(https://chiarapicardii.github.io/LeopardiTEIConversion/#fnref:1).

---

## Issue 2: Title apparatus

**Problem:** The titles have different versions across witnesses, this information needs to be preserved in the extraction.

**Solution:** the function `extract_structured_title()` uses the regualar expression `re.findall()` to collect all the cases with `[[Titolo:edition|text]]` patterns. Then the first match becomes the `<lem>` 
and the others the `<rdg>` elements.

```python
titles = re.findall(r"\[\[Titolo:([^|\]]+)\|([^\]]+)\]\]", wikitext, re.DOTALL)

base_edition, base_text = titles[0] #[0] is the first match

# If only one title, no apparatus needed
if len(titles) == 1:
    return f'<head>{base_text}</head>'

# Otherwise build the full apparatus
app_editions = []
for edition, text in titles[1:]:
    app_editions.append(f'<rdg wit="#{edition}">{text}</rdg>')

return f'<head><app><lem wit="#{base_edition}">{base_text}</lem>{"".join(app_editions)}</app></head>'
```

**Fallback:** when the extracted title is a lone Roman numeral (e.g. `IV`), which was a recurring WikiLeopardi formatting issue encountered, the function falls back to the JSON key.

```python
if not re.fullmatch(r'[IVXLCDM]+', clean_title):
    return clean_title
# else: use clean_fallback from JSON key
```

---

## Issue 3: Critical apparatus handling

**Problem:** WikiLeopardi encodes variants in three distinct patterns that must all be mapped to TEI `<app>` elements.

**Solution:** The function `replace_wit()` applies three sequential regex substitutions, each suited to the specific case.

**Case 1. Explicit witness: `[[Acronym:Variant|Lemma]]`** 

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

**Case 2. Pipe without acronym: `[[Variant|Lemma]]`**

This requires a further specification: when the variant contains the `<lb/>`, the element is removed and flattened to a single string. This is a necessary technical compromise to 
allow EVT to render the text, because it would have otherwise broken the apparatus strucuture. 

```python
def pipe(match):
    lem = clean(match.group(2))
    rdg = clean(match.group(1))
    if "<lb/>" in rdg or "\n" in rdg:
        clean_rdg = rdg.replace("<lb/>", " ").replace("\n", " ") #replacing the <lb/>
        return (
            f'<app><lem wit="#{main_witness}">{lem}</lem>'
            f'<rdg wit="{secondary_wits_string}">{clean_rdg}</rdg></app>'
        )
    return avoid_repetition_apparatus(lem, rdg, secondary_wits_string)
```

**Case 3. Plain link: `[[text]]`**

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

**Deduplication**
Sometimes, in the raw files, there were variants syntax containing the same text as the main witness used, so `avoid_repetition_apparatus` checks for repetitions and authomatically deletes them.

```python
def avoid_repetition_apparatus(lem, rdg, wit):
    if lem == rdg:
        return lem  # no apparatus needed: identical readings
    return f'<app><lem wit="#{main_witness}">{lem}</lem><rdg wit="{wit}">{rdg}</rdg></app>'
```

---

## Issue 4: Prose and poetry division

**Problem:** The corpus contains not only poems but also authorial notes, letters, and annotations, each requiring a different TEI structure.

**Solution:** The function `encode_div()` determines the `div_type` based on the keywords in the JSON keys, and divides the files in prose and poems, which are then processed accordingly.

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
## Issue 5: Metric encoding

**Problem:** WikiLeopardi stores verse numbers inline with the text, so they need be separated and converten in the TEI `n=` attribute without corrupting adjacent apparatus elements.

**Solution:** The function `isolate_verse_num()` uses a negative-lookbehind regular expression to distinguish verse numbers from page references, footnote numbers, and attribute values.

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

Metrically indented lines preserve `rend="indent"` as a TEI attribute, which was already processed in the text through the pre-processing script. 

---

*Scripts and data are openly available under CC BY 4.0.*  
*Encoded by Chiara Picardi — University of Bologna, 2025–26.*

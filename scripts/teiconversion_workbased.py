# Work-based TEI conversion for Leopardi's Canti (F31).
#
# Unlike teiconversion.py (which emits ONE TEI file per source PAGE), this script
# groups the paginated source into WORKS: one TEI document per canto/poem, with
# <pb/> page-breaks kept *inside* a single <div type="poem">, authorial notes
# nested as child <div type="note"> elements, and the prefatory Lettera as its
# own <div type="letter">.
#
# It reuses the leaf functions of teiconversion.py (preprocess_body, replace_wit,
# encode_verses, isolate_verse_num, extract_* ...) and adds:
#   1. page -> work grouping (by roman numeral);
#   2. an apparatus de-duplication fix (strip_shared_trailing) that removes the
#      shared trailing word wrongly kept inside <rdg> (the 297-hit bug).
#
# Run from the repository root:  python3 scripts/teiconversion_workbased.py

import re
import sys
import json
from pathlib import Path
from collections import defaultdict

# import the leaf functions of the page-based converter (import-safe: it is
# guarded by if __name__ == "__main__")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teiconversion as tc

INPUT_FILE = Path("clean_corpus.json")
OUTPUT_FOLDER = Path("F31_works")
MAIN_WITNESS = tc.main_witness  # "F31"
POEM_TAG = tc.poem_tag          # "<poem>"

ROMAN_RE = re.compile(r'(?:CANTO\s+)?([IVXLC]+)\b')


# --------------------------------------------------------------------------
# 1. Apparatus de-duplication fix
# --------------------------------------------------------------------------
# The source uses a compact convention:  [[FULL_READING|SHORT_LEMMA]] shared...
# e.g.  [[Della festa|De la]] festa che viene
# The other witnesses read "Della festa"; F31 reads "De la festa"; the shared
# word "festa" sits once, correctly, outside the brackets. The page-based
# converter copied the *full* reading into <rdg> ("Della festa") while the shared
# word also stayed in the running text -> "...</rdg></app> festa" (duplication).
#
# This pass detects, for every <rdg>...</rdg></app> immediately followed by
# running text, the longest word-aligned overlap between the reading's suffix and
# the following text's prefix, and strips it from the <rdg> so the shared word
# appears exactly once (outside the apparatus).

def _norm_word(w: str) -> str:
    return re.sub(r"[^0-9a-zàèéìòùáíóúäöü’']", "", w.lower())

_RDG_TRAIL_RE = re.compile(r'(<rdg\b[^>]*>)([^<]*?)(</rdg></app>)([^<\n]*)')


def strip_shared_trailing(text: str) -> str:
    def repl(m: re.Match) -> str:
        rdg_open, reading, close, after = m.groups()
        rwords = reading.split()
        awords = after.split()
        if not rwords or not awords:
            return m.group(0)
        maxk = min(len(rwords), len(awords))
        best = 0
        for i in range(1, maxk + 1):
            suffix = [_norm_word(x) for x in rwords[-i:]]
            prefix = [_norm_word(x) for x in awords[:i]]
            if suffix == prefix and all(prefix):
                best = i
        if best:
            new_reading = ' '.join(rwords[:-best]).strip()
            if new_reading:  # never empty the reading
                return f'{rdg_open}{new_reading}{close}{after}'

        # Elision case: the shared word is fused into the reading's last token by
        # an apostrophe, e.g. reading "Dell’ultimo" + trailing "ultimo" -> keep
        # the article "Dell’" and let "ultimo" stand once outside.
        elide = re.match(r"^(.*[’'])([^’'\s]+)$", rwords[-1])
        if elide and _norm_word(elide.group(2)) and _norm_word(elide.group(2)) == _norm_word(awords[0]):
            new_last = elide.group(1)
            new_reading = ' '.join(rwords[:-1] + [new_last]).strip()
            if new_reading:
                return f'{rdg_open}{new_reading}{close}{after}'
        return m.group(0)

    return _RDG_TRAIL_RE.sub(repl, text)


# --------------------------------------------------------------------------
# 2. Per-page body rendering (no per-page div / header wrapper)
# --------------------------------------------------------------------------

def _preclean(raw_text: str) -> str:
    t = raw_text or ""
    t = re.sub(r'\[\[\s*Edizione critica\s*\|?\s*\]\]', '', t, flags=re.IGNORECASE)
    t = re.sub(r'F31\s+[IVXLCDM]+\.?<lb/>[IVXLCDM]+\.?<lb/>', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[IVXLCDM]+\.\s+ALLA\s+PRIMAVERA,\s+O\s+DELLE\s+FAVOLE\s+ANTICHE\.', '', t)
    return t


def _process_page(raw_text: str):
    """Return (pb_lines, body_text, facs_files) for one source page."""
    facs = tc.extract_facsimiles(raw_text)
    t = _preclean(raw_text)
    t = tc.preprocess_body(t)
    t = tc.insert_pb(t, facs)
    t = tc.isolate_verse_num(t)

    pb_lines = re.findall(r'(<pb\s+[^>]+/>)', t)
    t = re.sub(r'<pb\s+[^>]+/>', '', t)

    if POEM_TAG in t:
        _, body = t.split(POEM_TAG, 1)
    else:
        body = t
    body = body.replace('</poem>', '')
    return pb_lines, body, facs


def _render_poem_verses(body: str, witnesses) -> str:
    body = re.sub(r'^\s*\(\)\s*', '', body.strip())
    body = re.sub(r"\[\[Titolo:.*?\]\]\s*", "", body, flags=re.DOTALL)
    body = tc.replace_wit(body, witnesses, MAIN_WITNESS)
    body = re.sub(r'<app>\s*<lem\s+[^>]*>[IVXLCDM]+\.?</lem>.*?</app>\s*\n?', '', body, flags=re.DOTALL)
    body = tc.isolate_verse_num(body)
    body = re.sub(r'^[IVXLCDM]+\.\s*', '', body)
    body = re.sub(r'<pb\s+[^>]+/>\s*', '', body)
    body = strip_shared_trailing(body)          # <-- the de-duplication fix
    return tc.encode_verses(body)


def _render_note_paragraphs(body: str, witnesses) -> str:
    t = body
    t = re.sub(r'F31\s+[IVXLCDM]+\.?<lb/>', '', t)
    t = re.sub(r'\[\[\s*Edizione critica\s*\|?\]\]', '', t)
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'(NOTA|NOTE)\.?(?:rend="indent")?\s*(?:\(\))?', '', t, flags=re.IGNORECASE)
    t = re.sub(r"\[\[Titolo:[^\]]*\]\]\s*", "", t)
    t = tc.replace_wit(t, witnesses, MAIN_WITNESS)
    t = re.sub(r'<app>\s*<lem[^>]*>[IVXLCDM]+\.?</lem>.*?</app>\s*\n?', '', t, flags=re.DOTALL)
    t = strip_shared_trailing(t)                # <-- de-duplication fix (prose too)
    t = t.replace("'", "’")
    t = re.sub(r'\(\)\s*', '', t)
    t = re.sub(r'<font[^>]*>', '', t, flags=re.IGNORECASE)
    t = t.strip()

    blocks = []
    for para in t.split("\n\n"):
        if not para.strip():
            continue
        has_indent = bool(re.search(r'rend=["”]?indent["”]?', para))
        clean_p = re.sub(r'rend=["”]?indent["”]?\s*', '', para).strip()
        clean_p = re.sub(r'\s*\n\s*', ' ', clean_p)
        clean_p = clean_p.replace('<lb break="no"/>', '')
        clean_p = re.sub(r'/?poem>', '', clean_p)
        p_tag = '<p rend="indent">' if has_indent else '<p>'
        blocks.append(f'          {p_tag}{clean_p}</p>')
    return "\n".join(blocks)


def _title_from_key(json_key: str, roman: str) -> str:
    clean = re.sub(r'^[A-Z]\d{2}\s+', '', json_key)
    clean = re.sub(r'\s+p\.\s*\d+.*$', '', clean).strip()
    if roman:
        clean = re.sub(rf'^(?:CANTO\s+)?{roman}\.?\s+', '', clean, flags=re.IGNORECASE)
    return clean.strip()


def _work_head(first_poem_raw: str, roman: str, fallback: str) -> str:
    """Build the <head> for the whole work from the first poem page."""
    _, body, _ = _process_page(first_poem_raw)
    head = tc.extract_structured_title(body, fallback)

    # extract_structured_title occasionally mis-parses a multi-line title and
    # emits an <app> whose wit is free text (e.g. wit="#LA SERA...") — invalid
    # TEI. Detect that and fall back to the clean title taken from the JSON key.
    wits = re.findall(r'wit="([^"]*)"', head)
    invalid_wit = any(not re.fullmatch(r'#[A-Z]\d{2}', w) for w in wits)

    if "Title not found" in head or '<lb/>' in head or invalid_wit:
        title = _title_from_key(fallback, roman)
        return f'<head>{roman + ". " if roman else ""}{title}</head>'

    # Valid head: strip any leading roman ("X." or "CANTO X.") from the visible
    # title, then prepend the roman exactly once.
    if roman:
        head = re.sub(rf'(<head>|<lem[^>]*>)\s*(?:CANTO\s+)?{roman}\.?\s+', r'\1', head,
                      count=1, flags=re.IGNORECASE)
        head = head.replace("<head>", f"<head>{roman}. ", 1)
    # collapse any stray newlines/space runs inside the head
    head = re.sub(r'\s*\n\s*', ' ', head)
    head = re.sub(r'  +', ' ', head)
    return head


# --------------------------------------------------------------------------
# 3. Grouping the corpus into works
# --------------------------------------------------------------------------

def classify(json_key: str) -> str:
    kl = json_key.lower()
    if 'lettera' in kl:
        return 'letter'
    if re.search(r'\(?\bnot[ae]\b|annotazioni|commento', kl):
        return 'note'
    return 'poem'


def group_works(data: dict):
    works = defaultdict(list)     # work_id -> list of (page_num, kind, key)
    for key in data:
        kind = classify(key)
        m = ROMAN_RE.match(re.sub(r'^F31\s+', '', key))
        roman = m.group(1) if m else None
        work_id = roman if roman else make_letter_id(key)
        pm = re.search(r'p\.\s*(\d+)', key)
        page = int(pm.group(1)) if pm else 0
        works[work_id].append((page, kind, key))
    for wid in works:
        # order by page, then poem before note within the same page
        works[wid].sort(key=lambda t: (t[0], 0 if t[1] == 'poem' else 1))
    return works


def make_letter_id(key: str) -> str:
    return tc.make_safe_id(re.sub(r'\s+p\.\s*\d+.*$', '', re.sub(r'^F31\s+', '', key)))


# --------------------------------------------------------------------------
# 4. Corpus-wide witness dictionary (mirrors run_all fallback)
# --------------------------------------------------------------------------

def build_witness_index(data: dict):
    global_wits = set()
    canto_wits = defaultdict(set)
    for key, text in data.items():
        m = ROMAN_RE.match(re.sub(r'^F31\s+', '', key))
        roman = m.group(1) if m else make_letter_id(key)
        header_part = text.split(POEM_TAG, 1)[0] if POEM_TAG in text else text
        for w in tc.extract_witnesses(header_part):
            global_wits.add(w)
            canto_wits[roman].add(w)
    return global_wits, canto_wits


def resolve_witnesses(work_id, global_wits, canto_wits):
    current = sorted(canto_wits.get(work_id, set()))
    if not current or current == [MAIN_WITNESS]:
        body = sorted(global_wits - {MAIN_WITNESS})
        head = sorted(global_wits | {MAIN_WITNESS})
    else:
        body = current
        head = sorted(set(current) | {MAIN_WITNESS})
    return body, head


# --------------------------------------------------------------------------
# 5. Assembling one work document
# --------------------------------------------------------------------------

def _dedupe_pages(entries, data):
    """The source sometimes has several keys for the SAME page (e.g. 'p.65',
    'p. 65', 'p_65'), with near-identical content. Keep one per page number —
    the longest (most complete) — to avoid repeating whole stanzas."""
    best = {}
    for pg, k in entries:
        if pg not in best or len(data[k]) > len(data[best[pg]]):
            best[pg] = k
    return [(pg, best[pg]) for pg in sorted(best)]


def build_work(work_id, pages, data, body_wits, head_wits):
    poem_pages = _dedupe_pages([(pg, k) for pg, kind, k in pages if kind == 'poem'], data)
    note_pages = _dedupe_pages([(pg, k) for pg, kind, k in pages if kind == 'note'], data)
    letter_pages = _dedupe_pages([(pg, k) for pg, kind, k in pages if kind == 'letter'], data)

    all_facs = []
    seen_facs = set()

    def collect_facs(raw):
        for f in tc.extract_facsimiles(raw):
            if f['xml_id'] not in seen_facs:
                seen_facs.add(f['xml_id'])
                all_facs.append(f)

    # ---- main content ----
    if poem_pages:
        div_type = 'poem'
        first_key = poem_pages[0][1]
        head = _work_head(data[first_key], work_id, first_key)

        seen_pb = set()
        chunks = []
        for pg, key in poem_pages:
            raw = data[key]
            collect_facs(raw)
            pb_lines, body, _ = _process_page(raw)
            verses = _render_poem_verses(body, body_wits)
            pb_out = ""
            for pb in pb_lines:
                n = re.search(r'n="(\d+)"', pb)
                if n and n.group(1) in seen_pb:
                    continue
                if n:
                    seen_pb.add(n.group(1))
                pb_out += f'          {pb}\n'
            if verses.strip():
                chunks.append(pb_out + verses)
        body_inner = (
            f'        <head>{_strip_head_tags(head)}</head>\n'
            f'        <lg>\n' + "\n".join(chunks) + "\n"
            f'        </lg>'
        )
    elif letter_pages:
        div_type = 'letter'
        head = 'LETTERA'
        seen_pb = set()
        chunks = []
        for pg, key in letter_pages:
            raw = data[key]
            collect_facs(raw)
            pb_lines, body, _ = _process_page(raw)
            paras = _render_note_paragraphs(body, body_wits)
            pb_out = ""
            for pb in pb_lines:
                n = re.search(r'n="(\d+)"', pb)
                if n and n.group(1) in seen_pb:
                    continue
                if n:
                    seen_pb.add(n.group(1))
                pb_out += f'          {pb}\n'
            if paras.strip():
                chunks.append(pb_out + paras)
        body_inner = (
            f'        <head>{head}</head>\n' + "\n".join(chunks)
        )
    else:
        # a work made only of notes (rare) — treat notes as the body below
        div_type = 'note'
        head = 'NOTA'
        body_inner = f'        <head>{head}</head>'

    # ---- nested notes ----
    note_blocks = []
    for pg, key in note_pages:
        raw = data[key]
        collect_facs(raw)
        pb_lines, body, _ = _process_page(raw)
        paras = _render_note_paragraphs(body, body_wits)
        pb_out = "".join(f'          {pb}\n' for pb in pb_lines)
        note_id = tc.make_safe_id(key)
        note_blocks.append(
            f'        <div type="note" xml:id="{note_id}" corresp="#{work_safe_id(work_id, poem_pages, letter_pages)}">\n'
            f'{pb_out}'
            f'          <head>NOTA</head>\n'
            f'{paras}\n'
            f'        </div>'
        )

    work_id_attr = work_safe_id(work_id, poem_pages, letter_pages)
    inner = body_inner
    if note_blocks:
        inner = body_inner + "\n" + "\n".join(note_blocks)

    body_div = (
        f'      <div type="{div_type}" xml:id="{work_id_attr}">\n'
        f'{inner}\n'
        f'      </div>'
    )

    header = tc.generate_tei_header(_plain_title(head, work_id), head_wits)
    facsimile = tc.build_facsimile(all_facs)
    return tc.assemble_tei(header, facsimile, body_div)


def _strip_head_tags(head: str) -> str:
    m = re.search(r'<head>(.*)</head>', head, re.DOTALL)
    return m.group(1).strip() if m else head


def _plain_title(head, work_id):
    inner = _strip_head_tags(head)
    inner = re.sub(r'<[^>]+>', '', inner)
    inner = re.sub(r'\s+', ' ', inner).strip()
    return inner or (work_id or "Untitled")


def work_safe_id(work_id, poem_pages, letter_pages):
    ref = poem_pages[0][1] if poem_pages else (letter_pages[0][1] if letter_pages else work_id)
    base = re.sub(r'\s+p\.\s*\d+.*$', '', re.sub(r'^F31\s+', '', ref))
    return tc.make_safe_id(base)


# --------------------------------------------------------------------------
# 6. Main
# --------------------------------------------------------------------------

def main():
    if not INPUT_FILE.exists():
        sys.exit(f"Input {INPUT_FILE} not found — run from the repository root.")
    data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    global_wits, canto_wits = build_witness_index(data)
    works = group_works(data)

    ok = 0
    for work_id, pages in sorted(works.items()):
        try:
            body_wits, head_wits = resolve_witnesses(work_id, global_wits, canto_wits)
            xml = build_work(work_id, pages, data, body_wits, head_wits)
            fname = f"{work_safe_id(work_id, [(p,k) for p,kind,k in pages if kind=='poem'], [(p,k) for p,kind,k in pages if kind=='letter'])}.xml"
            (OUTPUT_FOLDER / fname).write_text(xml, encoding="utf-8")
            print(f" ✓ {fname}  ({len(pages)} pages)")
            ok += 1
        except Exception as e:
            print(f" ✗ {work_id}: {e}")
    print(f"\nDone: {ok}/{len(works)} works written to {OUTPUT_FOLDER}/")


if __name__ == "__main__":
    main()

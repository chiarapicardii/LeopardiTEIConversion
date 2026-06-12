# Leopardi TEI Conversion Pipeline

An automated conversion of scholarly data from the Wikidata to XML/TEI syntax applied to (**Wikileopardi**)[https://wikileopardi.altervista.org/wiki_leopardi/index.php?title=Wiki_Leopardi]'s _Canti_ collection, rendered for **EVT (Edition Visualization Technology)**, available here: [https://chiarapicardii.github.io/LeopardiEVTvisualization/](https://chiarapicardii.github.io/LeopardiEVTvisualization/#/readingText?p=page-TEI%5B1%5D-text%5B1%5D-body%5B1%5D-div%5B1%5D-div%5B1%5D-pb%5B1%5D&el=critical)

## Project Overview
Aimed at contribuiting to the standardization and interoperability of digital scholarly data, this project builds an open-source, reusable architecture for Giacomo Leopardi's _Canti_. 

## Repository Structure

The codebase is organized into modular scripts to ensure systematic error-checking at each processing layer:

```text
├── _config.yml               # Jekyll configuration for GitHub Pages
├── index.md                  # Scholarly and methodological report
├── README.md                 # Technical documentation
├── corpus_F31.json           # Raw extracted corpus data (1831 Florentine print)
├── clean_corpus.json         # Intermediate normalized JSON corpus
├── scripts/                  # Data migration pipeline
│   ├── LeopardiParsing.py    # Node 1: Data Extraction API
│   ├── cleaning.py           # Node 2: Syntactical Normalization
│   └── teiconversion.py      # Node 3: XML/TEI Semantic Mapping

├── F31ConvertedFiles/        # Converted files, pipeline output
│   └── [Converted XML/TEI files of Leopardi's Canti]

└── assets/
    └── css/
        └── style.scss        # Custom CSS

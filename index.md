# From WikiLeopardi to TEI: Conversion Pipeline for Leopardi's Canti
## State of the Art
As illustrated by Italia and Priore (2021), Leopardi’s literary corpora serve as an exemplar case study to explore the various possibilities offered by digital scholarly editions. The variety of his production, the multiplicity of variants and the amount of documentation by the author itself provide an excellent ground to investigate different scholarly approaches. 

Three projects show the state of the art and the flexibility of the digital space: 
* **WikiLeopardi** [^1]: An edition focused on didactical aspects, which allows the user to easily explore the *Canti* tradition through a wiki-based interface. The platform renders the encoded text directly as an HTML code for visualization, meaning both the user consulting the edition and the scholars curating it do not need highly specific digital expertise, addressing what still remains one of the thresholds to the non-analogic space within the scholarly community.
* **Leopardi Ecdosys** [^2]: Approaches the *Idilli* with a deep understanding of what computing can offer when applied to philology. The text is annotated with what is called stand-off markup—an external annotation layer that, while leaving the source text unaltered, gives room for greater expressiveness in representing the chronological stratification of the poet’s writing process.
* **Leopardi 3D** [^3]: Demonstrates a totally different perspective, focusing on the physical page as a space where traces of the author's writing can be recovered. Reflectance Transformation Imaging (RTI) technology, utilizing high-definition photography, makes visible the depth left by different pens on the page, offering what before was not only impossible but unthinkable as a scholarly tool.

What these case studies collectively reveal is the enormous potential of scholarly editions, but they also highlight one of its central challenges: the need for a shared standard. Without an interoperable and portable format, what still remains a great project loses every possibility of being re-evaluated, re-studied, and reintegrated into larger infrastructures. As Sahle (2016) clearly states, a digital edition is not merely a digitized text, but a scholarly product whose value is greatly increased by its digital functionalities. XML/TEI encoding offers a well-established starting point that allows scholars to employ a flexible markup process which is both machine-readable and human-interpretable, therefore opening up new possibilities for data processing and visualization.

## Objectives
Within this framework, and responding to the specific need for a common standard, this project was developed with a primary reference in mind: *Leggo Manzoni* [^4], a rigorous TEI-based digital edition framework by the University of Bologna. Specifically, the goal was to create an automated data migration pipeline capable of converting source texts from the WikiLeopardi format into a standardized XML structure. The ultimate purpose is to build a "Leggo Leopardi" counterpart while simultaneously providing an EVT visualization layer. This architecture guarantees a high level of validity for the underlying code, ensuring long-term shareability and sustainability. In compliance with open-source academic principles, the reusable scripts and the converted files will be made openly available, aiming to bridge the gap between collaborative scholarly experimentation and the digital necessity for technical rigor.

## Methodology
The pipeline of the project is structured into three sequential Python scripts designed to incrementally process the data; this choice allows for systematic error-checking at each stage. Specifically, they are divided into:
1. [**Data Extraction**](https://github.com/chiarapicardii/LeopardiTEIConversion/blob/main/scripts/LeopardiParsing.py): The script programmatically queries the WikiLeopardi API to collect and download the raw textual files from the source platform.
2. [**Pre-cleaning**](https://github.com/chiarapicardii/LeopardiTEIConversion/blob/main/scripts/cleaning.py): The second script isolates and normalizes most of the anomalies of MediaWiki’s syntax, significantly simplifying the complexity of the core conversion script.
3. [**TEI Conversion**](https://github.com/chiarapicardii/LeopardiTEIConversion/blob/main/scripts/teiconversion.py): The main script transforms the pre-processed wiki components into compliant XML/TEI elements and attributes.

To guarantee transparency and data reusability, the detailed technical challenges encountered and their relative programmatic solutions are documented within the repository’s GitHub README file. Additionally, it is important to note that Large Language Models (Gemini, Claude) were used as coding assistants to navigate wiki-specific syntax and to ensure compliance of the XML structure with TEI guidelines, while all methodological and philological decisions remained strictly with the author.

All the converted files are stored in the GitHub repository, available [here](https://github.com/chiarapicardii/LeopardiTEIConversion/tree/main/F31ConvertedFiles)

## Visualization
While the primary focus of the project rested on automating the back-end conversion process, implementing a human-readable visualization layer was deemed essential to demonstrate the data's structural viability. The EVT (Edition Visualization Technology) viewer was selected because it processes TEI/XML files natively without requiring intermediate transformations, offering an immediate environment for interacting with the newly generated corpus.

The interface features a split-screen layout that pairs the edited critical text with facsimile images of the original 1831 Florentine print edition. In critical text mode, EVT renders the apparatus dynamically: text variants are highlighted directly within the text, and clicking on a specific variant reveals the corresponding witnesses alongside the reading. Beyond user accessibility, these strict encoding requirements provide a built-in validation layer; the precision required for the software to parse the files correctly helps the editor identify structural inconsistencies across the entire corpus without the need to manually audit the raw XML source code. 

The EVT is available here: [EVT visualization of 1831 _Canti_](https://chiarapicardii.github.io/LeopardiEVTvisualization/#/readingText?p=page-TEI%5B1%5D-text%5B1%5D-body%5B1%5D-div%5B1%5D-div%5B1%5D-pb%5B1%5D&el=critical)

## Limitations
Finally, it is necessary to acknowledge one significant philological limitation inherited from the source dataset. WikiLeopardi’s original syntax does not systematically mandate the explicit declaration of the witness associated with each textual variant, leaving a substantial portion of the apparatus without any explicit witness attribution. This represents a critical gap for the construction of a robust scholarly edition. The conversion pipeline addresses both the explicit and the missing cases by programmatically assigning variants to all potential witnesses when an attribution is absent. While this automated fallback preserves the data schema, it still requires a subsequent phase of manual review to guarantee full philological authoritativeness.

## References
* Italia, P., & Priore, R. (2021). Leopardi: Wiki Leopardi, Leopardi Ecdosys, Leopardi 3D. *Griseldaonline*, 20(2), 65–75. https://doi.org/10.6092/issn.1721-4777/12420
* Italia, P., & Tomasi, F. (Eds.). (2019). *Leggo Manzoni*. Università di Bologna, DH.arc. https://projects.dharc.unibo.it/leggomanzoni/
* Italia, P. (Ed.). (2019). *Leopardi Ecdosys: Edizione genetica digitale del Quaderno napoletano degli Idilli*. https://leopardi.ecdosys.org/it/Home/
* Sahle, P. (2016). What is a scholarly digital edition?. In M. J. Driscoll & E. Pierazzo (eds.), *Digital Scholarly Editing: Theories, Models and Methods* (pp. 19–39). Open Book Publishers. https://doi.org/10.11647/OBP.0095.02
* University of Bologna. (2026). *Manoscritti digitali: Leopardi3D*. Alma Mater Studiorum. https://site.unibo.it/manoscrittidigitali/it/progetti/leopardi-3d
* Wiki Leopardi. (2020, April 30). *WikiLeopardi*. Extracted at 15:57, June 11, 2026, from http://wikileopardi.altervista.org/wiki_leopardi/index.php?title=Wiki_Leopardi&oldid=18631

---

[^1]: http://wikileopardi.altervista.org/wiki_leopardi/index.php?title=Wiki_Leopardi&oldid=18631
[^2]: https://leopardi.ecdosys.org/it/Home/
[^3]: https://site.unibo.it/manoscrittidigitali/it/progetti/leopardi-3d
[^4]: https://projects.dharc.unibo.it/leggomanzoni/

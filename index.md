STATE OF ART 
As illustrated by Italia and Priore (2021) Leopardi’s literary corpora serve as an exemplar case study to explore the various possibilities offered by the digital scholarly editions. The variety of his production, the multiplicity of variants and the amount of documentation by the author itself is a great ground to investigate different scholarly approaches.
Three projects show the state of the art and the flexibility of the digital space. 
•	Wikileopardi : an edition focused on the didactical aspects, which allows the user to easily explore the Canti tradition through a wiki-based interface. The platform renders the encoded text directly as an html code for visualization, meaning both the user consulting the edition and the scholars curating it don’t need specific digital expertise, which in the scholarly community still remains one of the thresholds to the non-analogic space. 

•	Leopardi Ecdosys , approaches the Idilli with a deep understanding of what the computing can offer when applied to philology. The text is annotated with what is called a stand-off markup an external annotation layer that, while leaving the source text unaltered, gives room for greater expressiveness in representing the chronological stratification of the poet’s writing process. 

•	Leopardi 3d , demonstrates a totally different perspective, with a focus on the physical page as a space traces of the authors writing can be recovered. The RTI (Reflectance Transformation Imaging) technology, with high definition photography makes visible the depth left by the different pens on the page, offering what before was not only impossible but unthinkable as a scholarly tool.
What these case studies collectively reveal is the enormous potential of scholarly edition, but they also highlight one of its central challenges: the need for a shared standard. Without any interoperable and portable format what still remains a great project loses every possibility of being revaluated, restudied and reintegrated in bigger projects. As Sahle (2016) clearly states, the digital edition is not merely a text digitized but a scholarly product whose values is greatly increased by the digital functionalities. 
XML/TEI encoding offers a well-established starting point that allows scholars to have a flexible markup process which is both machine-readable and human-interpretable, therefore opening up new possibilities for data processing and visualization.
Objectives 
Within this framework, with a specific need for a common standard, this project was developed with a primary reference in mind: Leggo Manzoni , a rigorous TEI-based digital edition by the University of Bologna. 
Specifically, the goal in mind was to create a pipeline of conversion from the Wikileopardi data format to the XML one, offering an automatic process aimed at building a Leggo Leopardi counterpart, while simultaneously offering an EVT visualization, which guarantees a level of validity to the code, allowing shareability and sustainability.
The reusable script and the converted files will be openly available, according to the open source academic approach and with the hope to help bridge the gap between scholarly experimentation and the digital necessity for rigor.
Methodology 
The pipeline of the project is structured in three sequential Python scripts designed to incrementally process the data; this choice allows for error-checking at each stage. 
1.	Data extraction: the script queries the Wikileopardi API to collect and download the raw textual files from the source platform 
2.	Pre-cleaning and normalization: the second script isolates and normalizes most of the anomalies of MediaWiki’s syntax, simplifying the complexity of the core conversion script 
3.	Tei Conversion: The main script transforms the pre-processed wiki components in XML/TEI elements and attributes 
To guarantee transparency and data reusability, the detailed technical challenges encountered and their respective solutions are documented in the repository’s GitHub ReadMe file. 
It is also important to note that LLMs (Gemini, Claude), were used as a coding tool to navigate wiki-specific syntax and to ensure compliance of the XML structure with TEI guidelines, while all the methodological decisions remained with the author. 
Visualization 
While the project had most interest in automating a conversion process, it was useful to offer a way of visualizing the files in a more human-readable way. The EVT (Edition Visualization Technology) viewer was chosen as it reads the TEI/XML without the need for an intermediate transformation, offering a space of consultation of the corpus the project is based on. 
The interface has both a split-screen pairing with the edited text and the facsimile images of the original 1831 Florentine print and, in critical text mode, renders the apparatus with highlighted variants directly in the text, and, just by clicking on it shows the corresponding witnesses alongside the reading. 
In addition, the encoding requirements for the software to work are useful as a built-in validation layer: the precision required helps in identifying inconsistencies across the corpus without the need to read the raw XML file. 
Limitations 
Finally, it is important to acknowledge one significant limitation of the project: WikiLeopardi’s syntax does not require to systematically specify the witness associated to each variant, leaving a substantial part of the apparatus without any explicit witness attribution. This is a critical gap for the construction of a solid scholarly edition. The conversion addresses both the explicit and the missing cases, assigning variants to all witnesses when the attribution is absent; however, it still requires a manual review to guarantee full philological authoritativeness. 
Reference 
Italia, P., & Priore, R. (2021). Leopardi: Wiki Leopardi, Leopardi Ecdosys, Leopardi 3D. Griseldaonline, 20(2), 65–75. https://doi.org/10.6092/issn.1721-4777/12420
Italia, P., & Tomasi, F.. (2019). Leggo Manzoni. Università di Bologna. DH.arc. https://projects.dharc.unibo.it/leggomanzoni/
Italia, P. (Ed.). (2019). Leopardi Ecdosys: Edizione genetica digitale del Quaderno napoletano degli Idilli. https://leopardi.ecdosys.org/it/Home/
Sahle, P. (2016). What is a scholarly digital edition?. In M. J. Driscoll & E. Pierazzo (eds.), Digital Scholarly Editing: Theories, Models and Methods (pp. 19–39). Open Book Publishers. https://doi.org/10.11647/OBP.0095.02
University of Bologna. “Manoscritti digitali”. Leopardi3D. https://site.unibo.it/manoscrittidigitali/it/progetti/leopardi-3d 
Wiki Leopardi. (2020, aprile 30). WikiLeopardi. Extracted at 15:57, june 11, 2026 da http://wikileopardi.altervista.org/wiki_leopardi/index.php?title=Wiki_Leopardi&oldid=18631. 

import os
import requests
from io import StringIO
from pathlib import Path
from datetime import datetime

# Implementing formal validation using the methodology described by A. Barbaresi
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    print("Error: The 'lxml' library is required for formal TEI validation.")
    print("Please install it by running: pip install lxml requests")
    HAS_LXML = False

# Configuration mapping your pipeline output
OUTPUT_FOLDER = Path("F31_canti")
LOCAL_SCHEMA_FILE = Path("tei_all.rng")
REPORT_FILE = Path("validation_report.txt")

# Official standard URL for the TEI All RelaxNG schema
TEI_RNG_URL = "https://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"

def run_tei_validation():
    if not HAS_LXML:
        return

    if not OUTPUT_FOLDER.exists():
        print(f"✗ Error: The folder '{OUTPUT_FOLDER}' does not exist. Run the conversion pipeline first.")
        return

    xml_files = list(OUTPUT_FOLDER.glob("*.xml"))
    if not xml_files:
        print(f"⚠ No XML files found in folder '{OUTPUT_FOLDER}'.")
        return

    # Dynamic list to accumulate logs for the final report file
    report_lines = []

    def log_and_print(message=""):
        """Helper function to print to terminal and store for the text file."""
        print(message)
        report_lines.append(message)

    log_and_print("=========================================================")
    log_and_print("      TEI P5 FORMAL VALIDATION ENGINE (RelaxNG)")
    log_and_print("      Based on Adrien Barbaresi's Methodology")
    log_and_print(f"      Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_and_print("=========================================================")
    
    # 1. Fetching or Loading the Schema
    if not LOCAL_SCHEMA_FILE.exists():
        log_and_print("1. Downloading official TEI All schema (Happens ONLY ONCE)...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(TEI_RNG_URL, headers=headers, timeout=30)
            response.raise_for_status()
            
            schema_text = response.text
            
            # Precise check: verify if it's strictly a web error page format
            if schema_text.strip().startswith("<!DOCTYPE html") or schema_text.strip().startswith("<html"):
                log_and_print("✗ Error: The server returned an HTML page instead of the XML schema.")
                return

            LOCAL_SCHEMA_FILE.write_text(schema_text, encoding="utf-8")
            log_and_print("✓ Schema successfully downloaded and cached locally as 'tei_all.rng'.")
        except Exception as e:
            log_and_print(f"✗ Failed to download the TEI schema: {e}")
            return
    else:
        log_and_print("1. Loading TEI All schema from local cache ('tei_all.rng')...")
        schema_text = LOCAL_SCHEMA_FILE.read_text(encoding="utf-8")

    # 2. Compiling the Schema
    log_and_print("\n⏳ Compiling RelaxNG Schema...")
    log_and_print("   [Note: TEI All is massive. This can take 30-90 seconds. Please do not close!]")
    try:
        schema_text = schema_text.replace('<?xml version="1.0" encoding="utf-8"?>', '<?xml version="1.0"?>', 1)
        schema_text = schema_text.replace('<?xml version="1.0" encoding="UTF-8"?>', '<?xml version="1.0"?>', 1)
        
        # Parse using Barbaresi's StringIO method
        rng_doc = etree.parse(StringIO(schema_text))
        rng_validator = etree.RelaxNG(rng_doc)
        log_and_print("✓ RelaxNG Schema successfully compiled and ready!\n")
    except Exception as e:
        log_and_print(f"✗ Critical error during schema compilation: {e}")
        log_and_print("💡 Tip: Try deleting 'tei_all.rng' manually and run the script again.")
        return

    log_and_print(f"2. Starting validation scan for {len(xml_files)} files...")
    log_and_print("-" * 57)

    valid_files = 0
    invalid_files = 0

    for xml_file in xml_files:
        log_and_print(f"📄 File: {xml_file.name}")
        try:
            doc = etree.parse(str(xml_file))
            
            if rng_validator.validate(doc):
                log_and_print("   ↳ ✓ VALID: Perfect structure and fully compliant with TEI P5!")
                valid_files += 1
            else:
                log_and_print("   ↳ ✗ INVALID: Schema compliance errors found:")
                for error in rng_validator.error_log:
                    log_and_print(f"       [Line {error.line}, Col {error.column}]: {error.message}")
                invalid_files += 1

        except etree.XMLSyntaxError as e:
            log_and_print("   ↳ ✗ CRITICAL XML SYNTAX ERROR (Well-formedness):")
            log_and_print(f"       {e}")
            invalid_files += 1
        log_and_print("-" * 57)

    # Final summary report
    log_and_print("\n=========================================================")
    log_and_print("                    FINAL VALIDATION REPORT")
    log_and_print("=========================================================")
    log_and_print(f" Total files analyzed: {len(xml_files)}")
    log_and_print(f" Validated files (100% TEI P5): {valid_files}")
    log_and_print(f" Files with errors: {invalid_files}")
    log_and_print("=========================================================")
    
    if invalid_files == 0:
        log_and_print("🏆 EXCELLENT! All files are perfectly compliant and ready for EVT!")
    else:
        log_and_print("⚠ Validation finished with errors. Please check the logs above.")
        
    # Write output log to text file
    try:
        REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")
        print(f"\n💾 Validation report successfully saved to: {REPORT_FILE}")
    except Exception as e:
        print(f"\n✗ Failed to write validation report file: {e}")

if __name__ == "__main__":
    run_tei_validation()
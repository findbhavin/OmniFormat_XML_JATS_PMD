======================================================================
OmniJAX JATS 1.3 Publishing DTD Conversion Package
======================================================================

GENERATED FILES:
--------------------------------------------------
1. article.xml           - JATS 1.3 Publishing DTD XML (without DOCTYPE)
2. articledtd.xml        - JATS XML with DOCTYPE for PMC Style Checker
3. published_article.pdf - PDF generated from JATS XML
4. direct_from_word.pdf  - Direct DOCX→PDF conversion
5. article.html          - HTML version for web viewing
6. media/                - Extracted images and media files
7. validation_report.json- Comprehensive validation report
8. README.txt            - This file

COMPLIANCE INFORMATION:
--------------------------------------------------
• JATS 1.3 Publishing DTD compliant
• Official Schema: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
• PMC/NLM Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/
• PMC Style Checker ready for validation
• Table positioning: float/anchor (PMC compliant)
• MathML 2.0/3.0 support included
• Proper XLink namespace declarations
• Accessibility features (alt-text, captions)
• Media extraction to separate folder

PMC SUBMISSION CHECKLIST:
--------------------------------------------------
1. ✓ Use articledtd.xml for PMC Style Checker validation:
   https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
   (articledtd.xml includes DOCTYPE declaration required by PMC)
2. ✓ Use article.xml for XSD validation
3. ✓ Review validation_report.json for warnings
4. ✓ Verify DOI and article metadata are complete
5. ✓ Check author affiliations and ORCID IDs
6. ✓ Ensure all figures have captions and alt text
7. ✓ Verify references are properly formatted
8. ✓ Review table formatting (captions, structure)
9. ✓ Validate special characters and math notation

TECHNICAL DETAILS:
--------------------------------------------------
• Input file: 20260121_075548_ba13a931_10._Uma_Phalswal_5599_SYSMETA.docx
• Generated: 2026-01-21T07:57:24.438199
• JATS Version: 1.3 Publishing DTD
• Tools: Pandoc 3.x, WeasyPrint, lxml
• Schema: JATS-journalpublishing-oasis-article1-3-mathml2.xsd
• AI-enhanced content repair applied
• PMC compliance checks performed

VALIDATION DETAILS:
--------------------------------------------------
The XML has been validated against:
1. JATS Publishing DTD schema (XSD)
2. PMC-specific structural requirements
3. Required metadata elements
4. Table and figure formatting rules
5. Reference structure compliance

See validation_report.json for detailed results.

USAGE NOTES:
--------------------------------------------------
1. The JATS XML is validated against official schema
2. Two PDF versions are provided:
   - published_article.pdf: From JATS XML (semantic)
   - direct_from_word.pdf: Direct conversion (visual)
3. All images are extracted to media/ folder
4. Review validation_report.json before submission
5. Use PMC Style Checker for final validation
6. Check PMC tagging guidelines for specific requirements

REFERENCES:
--------------------------------------------------
• JATS Official: https://jats.nlm.nih.gov/
• PMC Tagging Guidelines:
  https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
• PMC Style Checker:
  https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
• JATS Publishing DTD:
  https://public.nlm.nih.gov/projects/jats/publishing/1.4/

SUPPORT:
--------------------------------------------------
OmniJAX Professional JATS Converter
PMC-Compliant Document Conversion System

======================================================================

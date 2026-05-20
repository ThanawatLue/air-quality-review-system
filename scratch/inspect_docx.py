from docx import Document

doc = Document(r"d:\ex_work\AirQualityReview_Project\validation_docs\csv_team_format\Appendix 3_Integration\Appendix 3_Enclosure 1.docx")
for i, p in enumerate(doc.paragraphs[:20]):
    print(f"Para {i}: '{p.text}'")
    num_pr = p._element.xpath('.//w:numPr')
    if num_pr:
        print(f"  -> Has numPr: {num_pr}")
        # Try to find ilvl and numId
        ilvl = p._element.xpath('.//w:ilvl/@w:val')
        numId = p._element.xpath('.//w:numId/@w:val')
        print(f"  -> ilvl: {ilvl}, numId: {numId}")
    print("-" * 20)

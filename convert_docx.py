import mammoth

docx_path = r"C:\Users\thana\My Drive\GPO\Appendix 2_Module\Appendix 2_Enclosure 1.docx"
md_path = r"C:\Users\thana\My Drive\GPO\Appendix 2_Module\Appendix 2_Enclosure 1.md"

with open(docx_path, "rb") as docx_file:
    result = mammoth.convert_to_markdown(docx_file)
    with open(md_path, "w", encoding="utf-8") as md_file:
        md_file.write(result.value)

print(f"Success! Converted to {md_path}")

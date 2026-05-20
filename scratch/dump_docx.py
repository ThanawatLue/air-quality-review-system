from docx import Document
import sys

def dump_docx(path):
    doc = Document(path)
    for i, p in enumerate(doc.paragraphs):
        try:
            sys.stdout.buffer.write(f"[{i}] {p.text}\n".encode('utf-8'))
        except Exception as e:
            print(f"Error at [{i}]: {e}")

if __name__ == "__main__":
    dump_docx(sys.argv[1])

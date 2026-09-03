"""Convert Markdown files to PDF format - Simple Version"""

from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Customer Churn Prediction System', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_title(self, text):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 12, text.encode('latin1', 'replace').decode('latin1'), 0, 1, 'C')
        self.ln(5)

    def add_heading(self, text, level=1):
        if level == 1:
            self.set_font('Arial', 'B', 14)
            self.set_fill_color(200, 220, 255)
            self.cell(0, 10, text.encode('latin1', 'replace').decode('latin1'), 0, 1, 'L', 1)
        elif level == 2:
            self.set_font('Arial', 'B', 12)
            self.cell(0, 8, text.encode('latin1', 'replace').decode('latin1'), 0, 1, 'L')
        else:
            self.set_font('Arial', 'B', 11)
            self.cell(0, 7, text.encode('latin1', 'replace').decode('latin1'), 0, 1, 'L')
        self.ln(3)

    def add_text(self, text):
        self.set_font('Arial', '', 10)
        clean = text.encode('latin1', 'replace').decode('latin1')
        self.multi_cell(0, 6, clean)
        self.ln(2)

    def add_bullet(self, text):
        self.set_font('Arial', '', 10)
        clean = text.encode('latin1', 'replace').decode('latin1')
        self.cell(10, 6, '', 0, 0)
        self.cell(0, 6, '- ' + clean, 0, 1)

    def add_table_row(self, cells, bold=False):
        self.set_font('Arial', 'B' if bold else '', 8)
        col_width = self.w / len(cells)
        for cell in cells:
            clean = cell.encode('latin1', 'replace').decode('latin1')
            self.cell(col_width, 7, clean, 1, 0, 'C')
        self.ln()

def convert_md_to_pdf(md_file, pdf_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    in_table = False
    table_rows = []

    for line in lines:
        line = line.rstrip()

        if not line:
            if in_table and table_rows:
                pdf.add_table_row(table_rows[0], bold=True)
                for row in table_rows[1:]:
                    pdf.add_table_row(row)
                table_rows = []
                in_table = False
            continue

        if line.startswith('# ') and not line.startswith('## '):
            if in_table and table_rows:
                pdf.add_table_row(table_rows[0], bold=True)
                for row in table_rows[1:]:
                    pdf.add_table_row(row)
                table_rows = []
                in_table = False
            pdf.add_title(line[2:])

        elif line.startswith('## '):
            if in_table and table_rows:
                pdf.add_table_row(table_rows[0], bold=True)
                for row in table_rows[1:]:
                    pdf.add_table_row(row)
                table_rows = []
                in_table = False
            pdf.add_heading(line[3:], 1)

        elif line.startswith('### '):
            if in_table and table_rows:
                pdf.add_table_row(table_rows[0], bold=True)
                for row in table_rows[1:]:
                    pdf.add_table_row(row)
                table_rows = []
                in_table = False
            pdf.add_heading(line[4:], 2)

        elif line.startswith('#### '):
            if in_table and table_rows:
                pdf.add_table_row(table_rows[0], bold=True)
                for row in table_rows[1:]:
                    pdf.add_table_row(row)
                table_rows = []
                in_table = False
            pdf.add_heading(line[5:], 3)

        elif line.startswith('- ') or line.startswith('* '):
            pdf.add_bullet(line[2:])

        elif line.startswith('|'):
            in_table = True
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if not all(c.startswith('-') and c.endswith('-') for c in cells):
                table_rows.append(cells)

        elif line.startswith('```'):
            pass

        elif line.startswith('---'):
            if in_table and table_rows:
                pdf.add_table_row(table_rows[0], bold=True)
                for row in table_rows[1:]:
                    pdf.add_table_row(row)
                table_rows = []
                in_table = False
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

        else:
            if in_table and table_rows and not line.startswith('|'):
                pdf.add_table_row(table_rows[0], bold=True)
                for row in table_rows[1:]:
                    pdf.add_table_row(row)
                table_rows = []
                in_table = False
            clean = line.replace('**', '').replace('*', '')
            pdf.add_text(clean)

    if in_table and table_rows:
        pdf.add_table_row(table_rows[0], bold=True)
        for row in table_rows[1:]:
            pdf.add_table_row(row)

    pdf.output(pdf_file)
    print(f"Created: {pdf_file}")

if __name__ == "__main__":
    project_dir = r"C:\Users\Lenovo\Desktop\Yuktamedia\ML project\1st"

    convert_md_to_pdf(
        os.path.join(project_dir, "SYNOPSIS.md"),
        os.path.join(project_dir, "SYNOPSIS.pdf")
    )

    convert_md_to_pdf(
        os.path.join(project_dir, "DOCUMENTATION.md"),
        os.path.join(project_dir, "DOCUMENTATION.pdf")
    )

    print("\nDone! Both PDF files created.")

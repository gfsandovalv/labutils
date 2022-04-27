from email import header
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape
import pandas as pd

class MyDocument(Document):
    def __init__(self, doc_info=''):
        super().__init__()
        header_path = 'template/header.tex'
        self.preamble.append(Command('input', header_path))
        self.preamble.append(Command('usepackage', 'authblk'))
        if doc_info != '':       
            
            with open(doc_info) as file:
                lines = [line.rstrip() for line in file]
                
            title = lines[0].removeprefix('título:').lstrip()
            author = [auth.lstrip() for auth in lines[1].removeprefix('autores:').lstrip().split(',')]
            date = NoEscape(r'\today') if lines[2].removeprefix('fecha:').lstrip() == 'hoy' else lines[2].removeprefix('fecha:').lstrip()
            
            affil = lines[3].removeprefix('universidad:').lstrip()
        
            
            self.preamble.append(Command('title', title))
            for auth in author:
                self.preamble.append(Command('author', auth))
            self.preamble.append(Command('date', date))
            self.preamble.append(Command('affil', affil))
            self.append(NoEscape(r'\maketitle'))
        

            
        

    def fill_document(self):
        """Add a section, a subsection and some text to the document."""
        with self.create(Section('A section')):
            self.append('Some regular text and some ')
            self.append(italic('italic text. '))

            with self.create(Subsection('A subsection')):
                self.append('Also some crazy characters: $&#{}')


if __name__ == '__main__':

    # Document
    doc = MyDocument(doc_info='report_info.txt')

    # Call function to add text
    doc.fill_document()

    # Add stuff to the document
    with doc.create(Section('A second section')):
        doc.append('Some text.')

    #doc.generate_pdf('basic_inheritance', clean_tex=False)
    #tex = doc.dumps()  # The document as string in LaTeX syntax
    doc.generate_pdf(clean_tex=False)
    
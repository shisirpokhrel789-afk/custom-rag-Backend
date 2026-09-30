from pathlib import Path
import fitz

class DocumentParser:
    """Extract text from supported document formats"""
    file_extensions={".pdf",".txt"}

    def extract_text(self,file_path:str)->str:
        path=Path(file_path)

        extension=path.suffix.lower()
        
        if extension not in self.file_extensions:
            raise ValueError(f'Unsupported file type:{extension}')
        
        if extension==".pdf":
            return self._extract_pdf(path)
        return self._extract_text(path)
    
    def _extract_pdf(self,path:Path)->str:
        document=fitz.open(path)

        try:
            pages:list[str]=[]
            for page in document:
                pages.append(page.get_text())
            return "\n".join(pages)
        finally:
            document.close()

    def _extract_text(self,path:Path)->str:
        return path.read_text(
            encoding="utf-8",
            errors="ignore"

        )
        
doc_extract=DocumentParser()
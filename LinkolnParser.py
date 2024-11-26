
class LinkolnDocument:
    """Class representing a legal document with parsing and annotation capabilities."""

    def __init__(self, content):
        self.content = content
        self.annotations = []

    def add_annotation(self, text, link):
        """Adds an HTML annotation to the document."""
        self.annotations.append(f'<a href="{link}" target="_blank">{text}</a>')

    def get_annotated_content(self):
        """Returns the content with annotations."""
        for annotation in self.annotations:
            self.content += f"\n{annotation}"
        return self.content


class LinkolnDocumentFactory:
    """Factory for creating LinkolnDocument objects."""

    @staticmethod
    def create_document(content):
        """Creates a LinkolnDocument instance."""
        return LinkolnDocument(content)


class LinkolnParser:
    """Main parser class to process legal documents."""

    def __init__(self, strict_mode=False):
        self.strict_mode = strict_mode

    def parse(self, text):
        """Parses the given text and returns a LinkolnDocument."""
        document = LinkolnDocumentFactory.create_document(text)
        
        # Example: Add mock annotations
        if "Article" in text:
            document.add_annotation("Article 123", "https://example.com/article-123")
        if "Law" in text:
            document.add_annotation("Law 456", "https://example.com/law-456")
        
        return document


# Example usage:
if __name__ == "__main__":
    parser = LinkolnParser(strict_mode=True)
    input_text = "This is a document referring to Article 123 and Law 456."
    document = parser.parse(input_text)

    print("Annotated Content:")
    print(document.get_annotated_content())

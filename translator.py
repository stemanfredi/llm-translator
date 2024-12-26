import argparse
import ollama
import os
import shutil
import re
from pathlib import Path
import fitz  # PyMuPDF for PDF handling
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import html2text


class DocumentProcessor:
    def __init__(self, file_path, language, model_name, test_mode):
        self.file_path = Path(file_path)
        self.language = language
        self.model_name = model_name
        self.test_mode = test_mode
        self.dirs = None

    def create_directory_structure(self):
        """Create directory structure for document processing."""
        base_dir = self.file_path.parent / self.file_path.stem
        self.dirs = {
            "original": base_dir / "original",
            "translated": base_dir / self.language[:3].lower(),
            "images": base_dir / "images",
        }
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        return self.dirs

    def pdf_to_markdown(self):
        """Convert PDF to markdown chapters."""
        chapters = []
        try:
            doc = fitz.open(self.file_path)

            # Try to get chapters from bookmarks
            toc = doc.get_toc()
            if toc:
                for i, (level, title, page) in enumerate(toc):
                    start_page = page - 1
                    end_page = toc[i + 1][2] - 1 if i < len(toc) - 1 else doc.page_count

                    text = ""
                    for pg in range(start_page, end_page):
                        text += doc[pg].get_text()

                    # Convert to markdown format
                    chapter_text = f"# {title}\n\n{text}"
                    chapters.append(chapter_text)
            else:
                # If no bookmarks, treat each page as a section
                text = ""
                for page in doc:
                    text += page.get_text()
                chapters = [text]  # Single chapter with all content

            doc.close()
            return chapters
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return None

    def epub_to_markdown(self):
        """Convert EPUB to markdown chapters."""
        chapters = []
        try:
            book = epub.read_epub(self.file_path)
            h = html2text.HTML2Text()
            h.body_width = 0  # No wrapping

            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # Convert HTML content to markdown
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    markdown = h.handle(str(soup))
                    chapters.append(markdown)

            return chapters
        except Exception as e:
            print(f"Error processing EPUB: {str(e)}")
            return None

    def split_markdown_into_chapters(self, content):
        """Split markdown content into chapters."""
        # Try splitting by # first
        chapters = re.split(r"\n(?=# )", content.strip())
        if len(chapters) == 1:
            # If no # headers, try ## headers
            chapters = re.split(r"\n(?=## )", content.strip())
        return chapters

    def process_markdown_images(self, content, is_translated=False):
        """Update image paths in markdown content."""
        image_pattern = r"!\[(.*?)\]\((.*?)\)"

        def replace_image_path(match):
            alt_text = match.group(1)
            image_path = match.group(2)

            # Extract image filename
            image_filename = os.path.basename(image_path)

            # Copy image to images directory if it exists
            original_image_path = Path(self.file_path).parent / image_path
            if original_image_path.exists():
                shutil.copy2(original_image_path, self.dirs["images"] / image_filename)

            # Return updated markdown image reference
            return f"![{alt_text}](../images/{image_filename})"

        return re.sub(image_pattern, replace_image_path, content)

    def translate_chapter(self, content):
        """Translate chapter content while preserving markdown formatting."""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Translate the following text to {self.language}. "
                            f"Preserve all markdown formatting, including headers (#), "
                            f"bold (**), italic (*), links, and images. "
                            f"Provide only the translation without explanations or notes:\n\n{content}"
                        ),
                    }
                ],
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return None

    def process_chapters(self, chapters):
        """Process and translate chapters."""
        for i, chapter in enumerate(chapters, 1):
            chapter_filename = f"chapter_{i:02d}.md"

            # Process original content
            processed_original = self.process_markdown_images(chapter)
            if not self.test_mode:
                self.write_file(
                    processed_original, self.dirs["original"] / chapter_filename
                )

            # Translate
            print(f"Translating chapter {i}...")
            translated = self.translate_chapter(chapter)
            if translated:
                processed_translation = self.process_markdown_images(
                    translated, is_translated=True
                )

                if self.test_mode:
                    print(f"\nChapter {i} translation:")
                    print("-" * 40)
                    print(processed_translation)
                    print("-" * 40)
                else:
                    self.write_file(
                        processed_translation,
                        self.dirs["translated"] / chapter_filename,
                    )

    def process(self):
        """Main processing method."""
        self.create_directory_structure()

        ext = self.file_path.suffix.lower()
        if ext == ".pdf":
            chapters = self.pdf_to_markdown()
        elif ext == ".epub":
            chapters = self.epub_to_markdown()
        elif ext in [".md", ".txt"]:
            content = self.read_file(self.file_path)
            chapters = self.split_markdown_into_chapters(content)
        else:
            print(f"Unsupported file type: {ext}")
            return

        if chapters:
            self.process_chapters(chapters)

    @staticmethod
    def read_file(file_path):
        """Read file content."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def write_file(content, file_path):
        """Write content to file."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Translate documents to a specified language."
    )
    parser.add_argument("--language", required=True, help="Target language")
    parser.add_argument("--model", default="mistral", help="LLM model name")
    parser.add_argument("--test", action="store_true", help="Test mode")
    parser.add_argument("file", help="Input file path")

    args = parser.parse_args()

    print(f"\nConfiguration:")
    print(f"-------------")
    print(f"Target language: {args.language}")
    print(f"Model: {args.model}")
    print(f"Input file: {args.file}")
    print(f"Mode: {'Testing' if args.test else 'Production'}")
    print()

    processor = DocumentProcessor(args.file, args.language, args.model, args.test)
    processor.process()


if __name__ == "__main__":
    main()

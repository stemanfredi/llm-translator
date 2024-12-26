# LLM Translator

A Python script that translates documents (PDF, EPUB, Markdown, and TXT) using the Ollama API while preserving document structure and formatting.

## Features

- Supports multiple document formats:
  - PDF (with bookmark-based chapter detection)
  - EPUB
  - Markdown
  - Text files
- Preserves document structure and formatting
- Handles images and updates their paths automatically
- Creates organized directory structure for translated content
- Supports test mode for preview translations
- Uses Ollama API for translations
- Maintains markdown formatting throughout the translation process

## Prerequisites

- Python 3.7+
- Ollama running locally (default port: 11434)

## Installation

1. Clone the repository:

```
git clone https://github.com/stemanfredi/llm-translator.git
cd llm-translator
```

2. Install required dependencies:

```
pip install ollama PyMuPDF EbookLib beautifulsoup4 html2text
```

3. Ensure Ollama is running on your system:

```
ollama serve
```

## Usage

Basic command structure:

```
python translator.py --language TARGET_LANGUAGE [--model MODEL_NAME] [--test] input_file
```

Examples:

```
# Translate PDF to Italian
python translator.py --language italian --model llama3.2 document.pdf

# Translate EPUB to Spanish with test mode
python translator.py --language spanish --model mistral --test book.epub

# Translate Markdown to French
python translator.py --language french --model llama3.2 content.md
```

### Command Line Arguments

- `--language`: Target language for translation (required)
- `--model`: Ollama model to use (default: "mistral-nemo")
- `--test`: Enable test mode (outputs translation to terminal instead of files)
- `file`: Input file path (required)

## Directory Structure

The script creates the following directory structure for processed files:

```
input_file_name/
├── original/
│   ├── chapter_01.md
│   ├── chapter_02.md
│   └── chapter_03.md
├── [language_code]/
│   ├── chapter_01.md
│   ├── chapter_02.md
│   └── chapter_03.md
└── images/
    ├── image1.jpg
    └── image2.png
```

## File Processing

### PDF Files

- Extracts chapters based on PDF bookmarks
- Falls back to single chapter if no bookmarks exist
- Converts content to markdown format

### EPUB Files

- Extracts chapters based on EPUB structure
- Converts HTML content to markdown format
- Preserves formatting during conversion

### Markdown/Text Files

- Splits content into chapters based on markdown headers (# or ##)
- Preserves existing markdown formatting
- Updates image references automatically

## Image Handling

- Automatically copies images to the `images/` directory
- Updates image references in markdown content
- Maintains relative paths for both original and translated versions

## Limitations

- Requires Ollama to be running locally
- PDF processing might not preserve complex layouts
- EPUB conversion might not handle all HTML formatting
- Translation quality depends on the chosen Ollama model

## Error Handling

The script includes error handling for:

- File not found
- Unsupported file types
- Translation API errors
- File read/write errors

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License.

## Acknowledgments

- [Ollama](https://github.com/ollama/ollama) for the translation API
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for PDF processing
- [EbookLib](https://github.com/aerkalov/ebooklib) for EPUB handling
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [html2text](https://github.com/Alir3z4/html2text) for HTML to Markdown conversion

## Support

For support, please open an issue in the GitHub repository.

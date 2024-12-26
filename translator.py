import argparse
import ollama
import os


def read_file(file_path):
    """Read content from a text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        exit(1)


def write_file(content, input_file, language):
    """Write translated content to a file."""
    try:
        # Get the directory and filename without extension
        directory = os.path.dirname(input_file)
        filename = os.path.splitext(os.path.basename(input_file))[0]

        # Create output filename: original_ita.txt (or other language code)
        lang_code = language[:3].lower()  # Take first 3 letters of language name
        output_file = os.path.join(directory, f"{filename}_{lang_code}.txt")

        # Write content to file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"\nTranslation saved to: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {str(e)}")
        exit(1)


def translate_text(text, target_language, model_name):
    """Translate text to the specified language using OLLAMA."""
    try:
        # Initialize OLLAMA client
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Please translate the following text to {target_language}. "
                        f"Maintain the original formatting and structure. "
                        f"Provide only the translation without explanations or notes:\n\n{text}"
                    ),
                }
            ],
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"Error during translation: {str(e)}")
        exit(1)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Translate text from a file to a specified language."
    )
    parser.add_argument(
        "--language", required=True, help="Target language for translation"
    )
    parser.add_argument(
        "--model",
        default="mistral-nemo",
        help="LLM model to use (default: mistral-nemo)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: output to screen instead of file",
    )
    parser.add_argument("file", help="Path to the text file to translate")

    # Parse arguments
    args = parser.parse_args()

    # Print selected configuration
    print(f"\nConfiguration:")
    print(f"-------------")
    print(f"Target language: {args.language}")
    print(f"Model: {args.model}")
    print(f"Input file: {args.file}")
    print(f"Mode: {'Testing' if args.test else 'Production'}")
    print()

    # Read the input file
    input_text = read_file(args.file)

    # Perform translation
    print("Translating...")
    translated_text = translate_text(input_text, args.language, args.model)

    # Handle output based on mode
    if args.test:
        print("\nTranslated text:")
        print("---------------")
        print(translated_text)
    else:
        write_file(translated_text, args.file, args.language)


if __name__ == "__main__":
    main()

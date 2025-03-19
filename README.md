# OpenAI File Search Implementation

This project implements the OpenAI Responses API file search tool for semantic search on PDF documents. It's based on the sample code that demonstrates using vector stores to search and answer questions from PDF content.

## Features

- Create vector stores on OpenAI
- Upload PDFs to the vector store
- Perform standalone vector searches
- Integrate search results with LLM responses
- Generate evaluation questions from PDFs
- Evaluate retrieval performance with metrics

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key as an environment variable:
   ```
   # On Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key-here"
   
   # On Linux/macOS
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

The implementation is provided as a Python module with a command-line interface:

### 1. Create a Vector Store

```
python search_api_implementation.py --action create_store --store_name "my_pdf_store" --output store_details.json
```

### 2. Upload PDFs to the Vector Store

```
python search_api_implementation.py --action upload --store_id "vs_123456789" --pdf_dir "path/to/pdfs" --output upload_stats.json
```

### 3. Perform Vector Search

```
python search_api_implementation.py --action search --store_id "vs_123456789" --query "What is Deep Research?"
```

### 4. Integrated LLM Search

```
python search_api_implementation.py --action llm_search --store_id "vs_123456789" --query "What is Deep Research?" --model "gpt-4o-mini"
```

### 5. Generate Evaluation Questions

```
python search_api_implementation.py --action generate_questions --pdf_dir "path/to/pdfs" --output questions.json
```

### 6. Evaluate Retrieval Performance

```
python search_api_implementation.py --action evaluate --store_id "vs_123456789" --output questions.json --k 5 --model "gpt-4o-mini"
```

## Project Structure

- `search_api_implementation.py`: Main implementation file
- `requirements.txt`: Python dependencies
- `README.md`: This documentation file

## Example Workflow

1. Create a vector store:
   ```
   python search_api_implementation.py --action create_store --store_name "openai_blog_store" --output store_details.json
   ```

2. Upload PDFs to the vector store:
   ```
   python search_api_implementation.py --action upload --store_id "vs_67d06b9b9a9c8191bafd456cf2364ce3" --pdf_dir "C:\Users\admin\ResponsesAPI\SearchOnThis" --output upload_stats.json
   ```

3. Generate questions for evaluation:
   ```
   python search_api_implementation.py --action generate_questions --pdf_dir "C:\Users\admin\ResponsesAPI\SearchOnThis" --output questions.json
   ```

4. Evaluate retrieval performance:
   ```
   python search_api_implementation.py --action evaluate --store_id "vs_67d06b9b9a9c8191bafd456cf2364ce3" --output questions.json --k 5
   ```

5. Perform search with LLM integration:
   ```
   python search_api_implementation.py --action llm_search --store_id "vs_67d06b9b9a9c8191bafd456cf2364ce3" --query "What is Deep Research?"
   ```

## Notes

- The API key is required for all operations
- Vector store IDs should be saved after creation for later use
- All PDF files in the specified directory will be processed
- Evaluation metrics include Recall, Precision, MRR, and MAP

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
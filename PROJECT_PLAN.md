# Project Plan: OpenAI File Search Implementation

## Project Overview

This project implements the OpenAI Responses API file search tool for semantic search on PDF documents. The implementation allows users to create vector stores, upload PDFs, search content, and evaluate retrieval performance.

## Objectives

1. Implement a modular, reusable solution for file search using OpenAI's Responses API
2. Create tools for uploading and managing PDF documents in OpenAI vector stores
3. Enable semantic search capabilities via direct vector search and LLM integration
4. Provide evaluation mechanisms to assess retrieval performance
5. Document the implementation with clear examples and usage instructions

## Implementation Details

### 1. Core Components

The project consists of the following core components:

#### `OpenAIFileSearch` Class

- **Purpose**: Main class that encapsulates all functionality
- **Key Methods**:
  - `create_vector_store`: Creates a new vector store on OpenAI
  - `upload_single_pdf`: Uploads a single PDF to a vector store
  - `upload_pdf_files_to_vector_store`: Uploads multiple PDFs in parallel
  - `vector_search`: Performs direct vector search
  - `llm_integrated_search`: Performs search with LLM integration
  - `extract_text_from_pdf`: Extracts text from PDFs
  - `generate_questions`: Generates evaluation questions from PDFs
  - `evaluate_retrieval`: Evaluates retrieval performance

#### Command-Line Interface

- **Purpose**: Provides easy access to all functionality
- **Actions**:
  - `create_store`: Create a new vector store
  - `upload`: Upload PDFs to a vector store
  - `search`: Perform vector search
  - `llm_search`: Perform integrated LLM search
  - `generate_questions`: Generate evaluation questions
  - `evaluate`: Evaluate retrieval performance

### 2. Workflow Implementation

The implementation follows a sequential workflow:

1. **Setup**:
   - Install dependencies
   - Configure OpenAI API key

2. **Vector Store Creation**:
   - Create a new vector store on OpenAI
   - Save store details for later use

3. **PDF Processing**:
   - Upload PDFs to the vector store
   - Handle concurrent uploads for efficiency

4. **Search Implementation**:
   - Direct vector search functionality
   - LLM-integrated search with annotations

5. **Evaluation**:
   - Generate questions from PDFs
   - Evaluate retrieval with metrics
   - Calculate recall, precision, MRR, and MAP

### 3. Technical Specifications

- **Language**: Python 3.8+
- **Dependencies**:
  - `openai`: OpenAI API client
  - `PyPDF2`: PDF parsing
  - `pandas`: Data manipulation
  - `tqdm`: Progress tracking
  - `concurrent-futures`: Parallel processing

- **API Requirements**:
  - OpenAI API key with access to Responses API
  - Permissions for file uploads and vector stores

### 4. Project Timeline

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Setup project structure and dependencies | 1 day |
| 2 | Implement core OpenAIFileSearch class | 2 days |
| 3 | Develop CLI interface | 1 day |
| 4 | Implement workflow scripts | 1 day |
| 5 | Testing and debugging | 2 days |
| 6 | Documentation and examples | 1 day |
| **Total** | | **8 days** |

## Testing Plan

### 1. Unit Testing

- Test each method of the `OpenAIFileSearch` class
- Verify correct API interactions
- Test error handling and edge cases

### 2. Integration Testing

- Test full workflow with sample PDFs
- Verify vector store creation and file uploads
- Test search functionality with various queries

### 3. Performance Testing

- Measure upload speeds with different file sizes
- Evaluate search response times
- Assess LLM integration performance

### 4. Evaluation Metrics

- Generate a test set of PDFs and questions
- Calculate and verify metrics:
  - Recall@k
  - Precision@k
  - Mean Reciprocal Rank (MRR)
  - Mean Average Precision (MAP)

## Deliverables

1. **Code**:
   - `search_api_implementation.py`: Main implementation
   - `requirements.txt`: Dependencies list

2. **Documentation**:
   - `README.md`: Usage instructions
   - `PROJECT_PLAN.md`: Project details and plan

3. **Scripts**:
   - `run_search_workflow.bat`: Windows batch script
   - `run_search_workflow.ps1`: PowerShell script

4. **Results Directory**:
   - `store_details.json`: Vector store information
   - `upload_stats.json`: Upload statistics
   - `questions.json`: Generated evaluation questions

## Usage Examples

### Creating a Vector Store and Uploading PDFs

```powershell
# Run the complete workflow
.\run_search_workflow.ps1
```

### Individual Components

```bash
# Create a vector store
python search_api_implementation.py --action create_store --store_name "my_store" --output results/store_details.json

# Upload PDFs
python search_api_implementation.py --action upload --store_id "vs_123456789" --pdf_dir "C:\Users\admin\ResponsesAPI\SearchOnThis" --output results/upload_stats.json

# Perform search
python search_api_implementation.py --action llm_search --store_id "vs_123456789" --query "What is Deep Research?"
```

## Future Enhancements

1. **Web Interface**:
   - Develop a simple web UI for easier interaction

2. **Advanced Filtering**:
   - Add metadata filtering capabilities
   - Implement result filtering by relevance score

3. **Batch Processing**:
   - Support for bulk processing operations
   - Scheduled updates of vector stores

4. **Result Visualization**:
   - Add visualization of search results
   - Display relevance scores and relationships

5. **Multi-format Support**:
   - Extend beyond PDFs to other document formats
   - Support for images and other media

## Conclusion

This project provides a comprehensive implementation of OpenAI's file search capabilities in the Responses API, enabling efficient semantic search across PDF documents. The modular design allows for easy extension and customization for various use cases. 
import os
import sys
import PyPDF2
import pandas as pd
import base64
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from openai import OpenAI
import argparse
import json

class OpenAIFileSearch:
    def __init__(self, api_key=None):
        """
        Initialize the OpenAI client with API key from environment variable or parameter
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass as parameter.")
        self.client = OpenAI(api_key=self.api_key)
        
    def create_vector_store(self, store_name):
        """
        Create a vector store on OpenAI API
        """
        try:
            vector_store = self.client.vector_stores.create(name=store_name)
            details = {
                "id": vector_store.id,
                "name": vector_store.name,
                "created_at": vector_store.created_at,
                "file_count": vector_store.file_counts.completed
            }
            print("Vector store created:", details)
            return details
        except Exception as e:
            print(f"Error creating vector store: {e}")
            return {}
            
    def upload_single_pdf(self, file_path, vector_store_id):
        """
        Upload a single PDF file to the vector store
        """
        file_name = os.path.basename(file_path)
        try:
            file_response = self.client.files.create(file=open(file_path, 'rb'), purpose="assistants")
            attach_response = self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_response.id
            )
            return {"file": file_name, "status": "success"}
        except Exception as e:
            print(f"Error with {file_name}: {str(e)}")
            return {"file": file_name, "status": "failed", "error": str(e)}
    
    def upload_pdf_files_to_vector_store(self, vector_store_id, dir_pdfs):
        """
        Upload multiple PDF files to the vector store in parallel
        """
        pdf_files = [os.path.join(dir_pdfs, f) for f in os.listdir(dir_pdfs) if f.lower().endswith('.pdf')]
        stats = {"total_files": len(pdf_files), "successful_uploads": 0, "failed_uploads": 0, "errors": []}
        
        print(f"{len(pdf_files)} PDF files to process. Uploading in parallel...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.upload_single_pdf, file_path, vector_store_id): file_path for file_path in pdf_files}
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(pdf_files)):
                result = future.result()
                if result["status"] == "success":
                    stats["successful_uploads"] += 1
                else:
                    stats["failed_uploads"] += 1
                    stats["errors"].append(result)

        return stats
    
    def vector_search(self, vector_store_id, query):
        """
        Perform a direct vector search query
        """
        try:
            search_results = self.client.vector_stores.search(
                vector_store_id=vector_store_id,
                query=query
            )
            return search_results
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return None
            
    def llm_integrated_search(self, vector_store_id, query, model="gpt-4o-mini", max_results=10):
        """
        Perform a search query integrated with LLM
        """
        try:
            response = self.client.responses.create(
                input=query,
                model=model,
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id],
                    "max_num_results": max_results,
                }]
            )
            
            # Extract annotations from the response
            annotations = response.output[1].content[0].annotations
                
            # Get retrieved filenames
            retrieved_files = set([result.filename for result in annotations])
            
            return {
                "files_used": list(retrieved_files),
                "response": response.output[1].content[0].text
            }
        except Exception as e:
            print(f"Error with LLM integrated search: {e}")
            return {"error": str(e)}
            
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text content from a PDF file
        """
        text = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
        return text

    def generate_questions(self, pdf_path):
        """
        Generate questions based on PDF content using OpenAI
        """
        text = self.extract_text_from_pdf(pdf_path)

        prompt = (
            "Can you generate a question that can only be answered from this document?:\n"
            f"{text}\n\n"
        )

        response = self.client.responses.create(
            input=prompt,
            model="gpt-4o",
        )

        question = response.output[0].content[0].text
        return question
        
    def evaluate_retrieval(self, vector_store_id, questions_dict, k=5, model="gpt-4o-mini"):
        """
        Evaluate retrieval performance using a set of questions
        """
        rows = []
        for filename, query in questions_dict.items():
            rows.append({"query": query, "_id": filename.replace(".pdf", "")})

        total_queries = len(rows)
        correct_retrievals_at_k = 0
        reciprocal_ranks = []
        average_precisions = []
        
        def process_query(row):
            query = row['query']
            expected_filename = row['_id'] + '.pdf'
            
            # Call file_search via Responses API
            response = self.client.responses.create(
                input=query,
                model=model,
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id],
                    "max_num_results": k,
                }],
                tool_choice="required"
            )
            
            # Extract annotations from the response
            annotations = None
            if hasattr(response.output[1], 'content') and response.output[1].content:
                annotations = response.output[1].content[0].annotations
            elif hasattr(response.output[1], 'annotations'):
                annotations = response.output[1].annotations

            if annotations is None:
                print(f"No annotations for query: {query}")
                return False, 0, 0

            # Get top-k retrieved filenames
            retrieved_files = [result.filename for result in annotations[:k]]
            if expected_filename in retrieved_files:
                rank = retrieved_files.index(expected_filename) + 1
                rr = 1 / rank
                correct = True
            else:
                rr = 0
                correct = False

            # Calculate Average Precision
            precisions = []
            num_relevant = 0
            for i, fname in enumerate(retrieved_files):
                if fname == expected_filename:
                    num_relevant += 1
                    precisions.append(num_relevant / (i + 1))
            avg_precision = sum(precisions) / len(precisions) if precisions else 0
            
            if expected_filename not in retrieved_files:
                print("Expected file NOT found in the retrieved files!")
                
            if retrieved_files and retrieved_files[0] != expected_filename:
                print(f"Query: {query}")
                print(f"Expected file: {expected_filename}")
                print(f"First retrieved file: {retrieved_files[0]}")
                print(f"Retrieved files: {retrieved_files}")
                print("-" * 50)
                
            return correct, rr, avg_precision
            
        with ThreadPoolExecutor() as executor:
            results = list(tqdm(executor.map(process_query, rows), total=total_queries))

        for correct, rr, avg_precision in results:
            if correct:
                correct_retrievals_at_k += 1
            reciprocal_ranks.append(rr)
            average_precisions.append(avg_precision)

        recall_at_k = correct_retrievals_at_k / total_queries
        precision_at_k = recall_at_k  # In this context, same as recall
        mrr = sum(reciprocal_ranks) / total_queries
        map_score = sum(average_precisions) / total_queries
        
        metrics = {
            f"recall@{k}": recall_at_k,
            f"precision@{k}": precision_at_k,
            "mrr": mrr,
            "map": map_score
        }
        
        return metrics

def main():
    parser = argparse.ArgumentParser(description="OpenAI File Search Implementation")
    parser.add_argument("--action", choices=["create_store", "upload", "search", "llm_search", "generate_questions", "evaluate"], 
                        required=True, help="Action to perform")
    parser.add_argument("--api_key", help="OpenAI API Key (optional, can use OPENAI_API_KEY env var)")
    parser.add_argument("--store_name", help="Name for the vector store")
    parser.add_argument("--store_id", help="Vector store ID")
    parser.add_argument("--pdf_dir", help="Directory containing PDF files")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use")
    parser.add_argument("--k", type=int, default=5, help="Number of results to retrieve")
    parser.add_argument("--output", help="Output file path for results")
    
    args = parser.parse_args()
    
    search_api = OpenAIFileSearch(api_key=args.api_key)
    
    if args.action == "create_store":
        if not args.store_name:
            print("Error: store_name is required for create_store action")
            return
        store_details = search_api.create_vector_store(args.store_name)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(store_details, f, indent=2)
                
    elif args.action == "upload":
        if not args.store_id or not args.pdf_dir:
            print("Error: store_id and pdf_dir are required for upload action")
            return
        stats = search_api.upload_pdf_files_to_vector_store(args.store_id, args.pdf_dir)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(stats, f, indent=2)
                
    elif args.action == "search":
        if not args.store_id or not args.query:
            print("Error: store_id and query are required for search action")
            return
        results = search_api.vector_search(args.store_id, args.query)
        # Format and print results
        for i, result in enumerate(results.data):
            print(f"Result {i+1}:")
            print(f"Filename: {result.filename}")
            print(f"Score: {result.score}")
            print(f"Content length: {len(result.content[0].text)}")
            print("---")
            
    elif args.action == "llm_search":
        if not args.store_id or not args.query:
            print("Error: store_id and query are required for llm_search action")
            return
        response = search_api.llm_integrated_search(args.store_id, args.query, model=args.model, max_results=args.k)
        print(f"Files used: {response.get('files_used', [])}")
        print("Response:")
        print(response.get('response', ''))
        
    elif args.action == "generate_questions":
        if not args.pdf_dir:
            print("Error: pdf_dir is required for generate_questions action")
            return
        pdf_files = [os.path.join(args.pdf_dir, f) for f in os.listdir(args.pdf_dir) if f.lower().endswith('.pdf')]
        questions_dict = {}
        for pdf_path in pdf_files:
            question = search_api.generate_questions(pdf_path)
            questions_dict[os.path.basename(pdf_path)] = question
            
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(questions_dict, f, indent=2)
        else:
            print(json.dumps(questions_dict, indent=2))
            
    elif args.action == "evaluate":
        if not args.store_id or not args.output:
            print("Error: store_id and output (questions JSON) are required for evaluate action")
            return
            
        with open(args.output, 'r') as f:
            questions_dict = json.load(f)
            
        metrics = search_api.evaluate_retrieval(
            args.store_id, 
            questions_dict, 
            k=args.k, 
            model=args.model
        )
        
        print(f"Metrics at k={args.k}:")
        print(f"Recall@{args.k}: {metrics[f'recall@{args.k}']:.4f}")
        print(f"Precision@{args.k}: {metrics[f'precision@{args.k}']:.4f}")
        print(f"Mean Reciprocal Rank (MRR): {metrics['mrr']:.4f}")
        print(f"Mean Average Precision (MAP): {metrics['map']:.4f}")
        
if __name__ == "__main__":
    main() 
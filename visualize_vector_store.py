#!/usr/bin/env python
"""
Visualize Vector Store

A command-line utility to create an OpenAI vector store, upload PDFs, and visualize the embeddings.

Usage:
    python visualize_vector_store.py create-and-visualize --store_name "my_store" --pdf_dir "path/to/pdfs" --output "visualization.html"
    python visualize_vector_store.py visualize --store_id "vs_your_vector_store_id" --output "visualization.html"
"""

import os
import sys
import argparse
import json
from dotenv import load_dotenv
from search_api_implementation import OpenAIFileSearch
from vector_store_visualizer import VectorStoreVisualizer

# Load environment variables from .env file
load_dotenv()

def create_store(args):
    """
    Create a new vector store
    """
    search_api = OpenAIFileSearch(api_key=args.api_key)
    store_details = search_api.create_vector_store(args.store_name)
    
    if not store_details:
        print("Error creating vector store.")
        return None
    
    print(f"Vector store created: {store_details['name']} (ID: {store_details['id']})")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(store_details, f, indent=2)
        print(f"Store details saved to {args.output}")
    
    return store_details['id']

def upload_pdfs(args, store_id):
    """
    Upload PDFs to the vector store
    """
    search_api = OpenAIFileSearch(api_key=args.api_key)
    stats = search_api.upload_pdf_files_to_vector_store(store_id, args.pdf_dir)
    
    print(f"Upload complete: {stats['successful_uploads']} successful, {stats['failed_uploads']} failed")
    
    if args.upload_stats:
        with open(args.upload_stats, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Upload stats saved to {args.upload_stats}")
    
    return stats['successful_uploads'] > 0

def visualize(args):
    """
    Visualize the vector store
    """
    visualizer = VectorStoreVisualizer(api_key=args.api_key)
    df = visualizer.visualize_vector_store(
        vector_store_id=args.store_id,
        max_results=args.max_results,
        output_file=args.output,
        run_dash=args.run_dash
    )
    
    if df is not None:
        print(f"Visualization complete with {len(df)} embeddings.")
        if args.output:
            print(f"Visualization saved to {args.output}")
        return True
    else:
        print("Error visualizing vector store.")
        return False

def create_and_visualize(args):
    """
    Create a vector store, upload PDFs, and visualize
    """
    # Create store
    store_id = create_store(args)
    if not store_id:
        return False
    
    # Upload PDFs
    if not upload_pdfs(args, store_id):
        print("Error uploading PDFs. Visualization may not show any data.")
    
    # Update store_id for visualization
    args.store_id = store_id
    
    # Visualize
    return visualize(args)

def main():
    parser = argparse.ArgumentParser(description="OpenAI Vector Store Visualization Utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--api_key", help="OpenAI API Key (optional, can use OPENAI_API_KEY env var)")
    parent_parser.add_argument("--env_file", default=".env", help="Path to .env file (default: .env)")
    
    # Create store command
    create_parser = subparsers.add_parser("create", parents=[parent_parser], help="Create a new vector store")
    create_parser.add_argument("--store_name", required=True, help="Name for the vector store")
    create_parser.add_argument("--output", help="Output file path for store details")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", parents=[parent_parser], help="Upload PDFs to a vector store")
    upload_parser.add_argument("--store_id", required=True, help="Vector store ID")
    upload_parser.add_argument("--pdf_dir", required=True, help="Directory containing PDF files")
    upload_parser.add_argument("--upload_stats", help="Output file path for upload stats")
    
    # Visualize command
    visualize_parser = subparsers.add_parser("visualize", parents=[parent_parser], help="Visualize a vector store")
    visualize_parser.add_argument("--store_id", required=True, help="Vector store ID")
    visualize_parser.add_argument("--max_results", type=int, default=1000, help="Maximum number of embeddings to retrieve")
    visualize_parser.add_argument("--output", help="Output HTML file path")
    visualize_parser.add_argument("--run_dash", action="store_true", help="Run Dash web application")
    
    # Create and visualize command (all-in-one)
    create_and_visualize_parser = subparsers.add_parser("create-and-visualize", parents=[parent_parser], help="Create a vector store, upload PDFs, and visualize")
    create_and_visualize_parser.add_argument("--store_name", required=True, help="Name for the vector store")
    create_and_visualize_parser.add_argument("--pdf_dir", required=True, help="Directory containing PDF files")
    create_and_visualize_parser.add_argument("--max_results", type=int, default=1000, help="Maximum number of embeddings to retrieve")
    create_and_visualize_parser.add_argument("--output", help="Output HTML file path")
    create_and_visualize_parser.add_argument("--upload_stats", help="Output file path for upload stats")
    create_and_visualize_parser.add_argument("--run_dash", action="store_true", help="Run Dash web application")
    
    args = parser.parse_args()
    
    # Load from specific .env file if provided
    if args.env_file and args.env_file != ".env":
        load_dotenv(args.env_file)
    
    # Execute the appropriate command
    if args.command == "create":
        create_store(args)
    elif args.command == "upload":
        upload_pdfs(args, args.store_id)
    elif args.command == "visualize":
        visualize(args)
    elif args.command == "create-and-visualize":
        create_and_visualize(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

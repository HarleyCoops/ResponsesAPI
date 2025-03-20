#!/usr/bin/env python
"""
Example Visualization Script

This script demonstrates how to use the vector store visualization module programmatically.
It provides examples of creating a vector store, uploading PDFs, and visualizing the embeddings.

Usage:
    python example_visualization.py
"""

import os
import sys
from dotenv import load_dotenv
from search_api_implementation import OpenAIFileSearch
from vector_store_visualizer import VectorStoreVisualizer

# Load environment variables from .env file
load_dotenv()

def example_create_and_visualize():
    """
    Example of creating a vector store, uploading PDFs, and visualizing
    """
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        return
    
    # Get PDF directory from user
    pdf_dir = input("Enter the directory containing PDF files to upload: ")
    if not os.path.exists(pdf_dir):
        print(f"Error: Directory '{pdf_dir}' does not exist.")
        return
    
    # Create a vector store
    print("\nCreating vector store...")
    search_api = OpenAIFileSearch(api_key=api_key)
    store_details = search_api.create_vector_store("Example Vector Store")
    
    if not store_details:
        print("Error creating vector store.")
        return
    
    store_id = store_details['id']
    print(f"Vector store created: {store_details['name']} (ID: {store_id})")
    
    # Upload PDFs
    print("\nUploading PDFs...")
    stats = search_api.upload_pdf_files_to_vector_store(store_id, pdf_dir)
    print(f"Upload complete: {stats['successful_uploads']} successful, {stats['failed_uploads']} failed")
    
    if stats['successful_uploads'] == 0:
        print("No PDFs were successfully uploaded. Visualization may not show any data.")
    
    # Visualize
    print("\nVisualizing vector store...")
    visualizer = VectorStoreVisualizer(api_key=api_key)
    
    # Example 1: Generate a static HTML visualization
    output_file = "example_visualization.html"
    df = visualizer.visualize_vector_store(
        vector_store_id=store_id,
        max_results=1000,
        output_file=output_file
    )
    
    if df is not None:
        print(f"Visualization saved to {output_file}")
        print(f"Visualization contains {len(df)} embeddings.")
        
        # Print cluster information
        cluster_counts = df['cluster'].value_counts()
        print("\nCluster information:")
        for cluster, count in cluster_counts.items():
            print(f"Cluster {cluster}: {count} documents")
    
    # Example 2: Run an interactive Dash web application
    run_dash = input("\nWould you like to run the interactive Dash web application? (y/n): ")
    if run_dash.lower() == 'y':
        print("\nStarting Dash web application...")
        visualizer.visualize_vector_store(
            vector_store_id=store_id,
            max_results=1000,
            run_dash=True
        )

def example_visualize_existing():
    """
    Example of visualizing an existing vector store
    """
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        return
    
    # Get vector store ID from user
    store_id = input("Enter the vector store ID: ")
    
    # Visualize
    print("\nVisualizing vector store...")
    visualizer = VectorStoreVisualizer(api_key=api_key)
    
    # Example 1: Generate a static HTML visualization
    output_file = "example_visualization.html"
    df = visualizer.visualize_vector_store(
        vector_store_id=store_id,
        max_results=1000,
        output_file=output_file
    )
    
    if df is not None:
        print(f"Visualization saved to {output_file}")
        print(f"Visualization contains {len(df)} embeddings.")
        
        # Print cluster information
        cluster_counts = df['cluster'].value_counts()
        print("\nCluster information:")
        for cluster, count in cluster_counts.items():
            print(f"Cluster {cluster}: {count} documents")
    
    # Example 2: Run an interactive Dash web application
    run_dash = input("\nWould you like to run the interactive Dash web application? (y/n): ")
    if run_dash.lower() == 'y':
        print("\nStarting Dash web application...")
        visualizer.visualize_vector_store(
            vector_store_id=store_id,
            max_results=1000,
            run_dash=True
        )

def example_programmatic_usage():
    """
    Example of programmatic usage of the visualization module
    """
    print("\nProgrammatic Usage Example")
    print("=========================")
    print("\nThis is an example of how to use the visualization module in your own Python code:")
    print("""
from vector_store_visualizer import VectorStoreVisualizer

# Initialize the visualizer
visualizer = VectorStoreVisualizer()

# Visualize a vector store
df = visualizer.visualize_vector_store(
    vector_store_id="vs_your_vector_store_id",
    max_results=1000,
    output_file="visualization.html",
    run_dash=True
)

# Access the DataFrame with visualization data
if df is not None:
    # Get the number of clusters
    num_clusters = len(df['cluster'].unique())
    print(f"Number of clusters: {num_clusters}")
    
    # Get the number of documents in each cluster
    cluster_counts = df['cluster'].value_counts()
    print("Cluster counts:")
    print(cluster_counts)
    
    # Get the documents in a specific cluster
    cluster_documents = df[df['cluster'] == 0]
    print(f"Documents in cluster 0: {len(cluster_documents)}")
    
    # Get the document with the highest x-coordinate
    max_x_document = df.loc[df['x'].idxmax()]
    print(f"Document with highest x-coordinate: {max_x_document['filename']}")
    """)

def main():
    print("OpenAI Vector Store Visualization Examples")
    print("=========================================")
    print("\nThis script demonstrates how to use the vector store visualization module.")
    print("\nChoose an example:")
    print("1. Create a vector store, upload PDFs, and visualize")
    print("2. Visualize an existing vector store")
    print("3. Show programmatic usage example")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        example_create_and_visualize()
    elif choice == "2":
        example_visualize_existing()
    elif choice == "3":
        example_programmatic_usage()
    elif choice == "4":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice.")
        sys.exit(1)

if __name__ == "__main__":
    main()

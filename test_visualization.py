#!/usr/bin/env python
"""
Test Visualization Script

This script tests the vector store visualization functionality.
It creates a mock vector store with random embeddings and visualizes them.

Usage:
    python test_visualization.py
"""

import os
import sys
import numpy as np
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from vector_store_visualizer import VectorStoreVisualizer

# Load environment variables from .env file
load_dotenv()

class MockVectorStoreVisualizer(VectorStoreVisualizer):
    """
    A mock version of the VectorStoreVisualizer that doesn't require an actual vector store.
    This is useful for testing the visualization functionality without needing to create a real vector store.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the mock visualizer
        """
        # Skip the parent class initialization to avoid requiring an API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or "mock_api_key"
    
    def fetch_embeddings(self, vector_store_id, max_results=1000):
        """
        Generate mock embeddings instead of fetching from a real vector store
        """
        print(f"Generating {max_results} mock embeddings...")
        
        # Generate random embeddings
        embeddings_data = []
        for i in range(max_results):
            # Create a random embedding vector (1536 dimensions for OpenAI embeddings)
            embedding = np.random.normal(0, 1, 1536)
            
            # Create mock metadata
            metadata = {
                "category": np.random.choice(["article", "blog", "documentation", "research"]),
                "author": np.random.choice(["Alice", "Bob", "Charlie", "David", "Eve"]),
                "date": f"2025-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}"
            }
            
            # Add to embeddings data
            embeddings_data.append({
                'id': f"doc_{i}",
                'filename': f"document_{i}.pdf",
                'embedding': embedding,
                'metadata': metadata,
                'text': f"This is a mock document {i} with random content for testing purposes."
            })
        
        return embeddings_data
    
    def get_vector_store_info(self, vector_store_id):
        """
        Return mock vector store info
        """
        return {
            "id": vector_store_id,
            "name": "Mock Vector Store",
            "created_at": "2025-03-20T12:00:00Z",
            "file_count": 1000
        }

def test_visualization():
    """
    Test the visualization functionality
    """
    print("Testing Vector Store Visualization")
    print("=================================")
    
    # Create a mock visualizer
    visualizer = MockVectorStoreVisualizer()
    
    # Generate a static HTML visualization
    output_file = "test_visualization.html"
    df = visualizer.visualize_vector_store(
        vector_store_id="mock_store_id",
        max_results=100,  # Use a smaller number for faster testing
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
        
        # Test if the visualization was created successfully
        if os.path.exists(output_file):
            print(f"\nTest passed: Visualization file {output_file} was created successfully.")
        else:
            print(f"\nTest failed: Visualization file {output_file} was not created.")
    else:
        print("Test failed: Visualization data frame is None.")
    
    # Ask if the user wants to run the interactive Dash web application
    run_dash = input("\nWould you like to run the interactive Dash web application? (y/n): ")
    if run_dash.lower() == 'y':
        print("\nStarting Dash web application...")
        visualizer.visualize_vector_store(
            vector_store_id="mock_store_id",
            max_results=100,  # Use a smaller number for faster testing
            run_dash=True
        )

if __name__ == "__main__":
    test_visualization()

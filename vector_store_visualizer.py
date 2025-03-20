"""
Vector Store Visualizer

This module provides functionality to visualize OpenAI vector stores in 3D space.
It retrieves embeddings from the vector store, performs dimensionality reduction,
applies clustering, and generates an interactive visualization.

Usage:
    python vector_store_visualizer.py --store_id "vs_your_vector_store_id" --output "visualization.html"
"""

import os
import sys
import argparse
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
import umap
import hdbscan
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from dash import Dash, html, dcc, callback, Output, Input

# Load environment variables from .env file
load_dotenv()

class VectorStoreVisualizer:
    def __init__(self, api_key=None):
        """
        Initialize the OpenAI client with API key from environment variable or parameter
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable, add it to .env file, or pass as parameter.")
        self.client = OpenAI(api_key=self.api_key)
        
    def get_vector_store_info(self, vector_store_id):
        """
        Get information about the vector store
        """
        try:
            vector_store = self.client.vector_stores.retrieve(vector_store_id=vector_store_id)
            return {
                "id": vector_store.id,
                "name": vector_store.name,
                "created_at": vector_store.created_at,
                "file_count": vector_store.file_counts.completed
            }
        except Exception as e:
            print(f"Error retrieving vector store info: {e}")
            return {}
    
    def fetch_embeddings(self, vector_store_id, max_results=1000):
        """
        Fetch embeddings from the vector store
        
        Since OpenAI's API doesn't directly expose the embeddings, we use a query with a 
        placeholder vector to retrieve nearest neighbors and their embeddings.
        """
        try:
            # Create a placeholder vector (all zeros) with the correct dimension (1536 for OpenAI embeddings)
            placeholder_vector = [0.0] * 1536
            
            # Query the vector store to get embeddings
            search_results = self.client.vector_stores.search(
                vector_store_id=vector_store_id,
                query_vector=placeholder_vector,
                max_results=max_results,
                include_values=True,  # Include the actual embedding values
                include_metadata=True  # Include metadata
            )
            
            # Process the results
            embeddings_data = []
            for result in search_results.data:
                # Extract the embedding values
                embedding = result.values if hasattr(result, 'values') else None
                
                # If embedding values are not available, try to get them from the score
                if not embedding and hasattr(result, 'score'):
                    # This is a fallback and may not be accurate
                    print("Warning: Using score as a proxy for embedding, which may not be accurate.")
                    embedding = [result.score]
                
                if embedding:
                    embeddings_data.append({
                        'id': result.id,
                        'filename': result.filename if hasattr(result, 'filename') else "Unknown",
                        'embedding': embedding,
                        'metadata': result.metadata if hasattr(result, 'metadata') else {},
                        'text': result.text if hasattr(result, 'text') else ""
                    })
            
            return embeddings_data
        except Exception as e:
            print(f"Error fetching embeddings: {e}")
            return []
    
    def reduce_dimensions(self, embeddings, n_components=3, n_neighbors=15, min_dist=0.1, metric='cosine'):
        """
        Reduce the dimensionality of embeddings using UMAP
        """
        try:
            # Create and fit the UMAP model
            reducer = umap.UMAP(
                n_components=n_components,
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                metric=metric,
                random_state=42
            )
            
            # Apply dimensionality reduction
            reduced_embeddings = reducer.fit_transform(embeddings)
            
            return reduced_embeddings
        except Exception as e:
            print(f"Error reducing dimensions: {e}")
            return None
    
    def apply_clustering(self, reduced_embeddings, min_cluster_size=5, min_samples=None, cluster_selection_epsilon=0.5):
        """
        Apply HDBSCAN clustering to the reduced embeddings
        """
        try:
            # Create and fit the HDBSCAN model
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                cluster_selection_epsilon=cluster_selection_epsilon,
                metric='euclidean'
            )
            
            # Apply clustering
            cluster_labels = clusterer.fit_predict(reduced_embeddings)
            
            return cluster_labels
        except Exception as e:
            print(f"Error applying clustering: {e}")
            return None
    
    def create_visualization_data(self, embeddings_data, reduced_embeddings, cluster_labels):
        """
        Create a DataFrame with visualization data
        """
        try:
            # Create a DataFrame with the reduced embeddings
            df = pd.DataFrame(reduced_embeddings, columns=['x', 'y', 'z'])
            
            # Add document information
            df['id'] = [data['id'] for data in embeddings_data]
            df['filename'] = [data['filename'] for data in embeddings_data]
            
            # Add metadata as separate columns
            for i, data in enumerate(embeddings_data):
                metadata = data.get('metadata', {})
                for key, value in metadata.items():
                    if key not in df.columns:
                        df[key] = None
                    df.at[i, key] = value
            
            # Add cluster labels
            df['cluster'] = cluster_labels
            
            # Add a text preview (first 100 characters)
            df['text_preview'] = [data.get('text', '')[:100] + '...' if data.get('text', '') else '' for data in embeddings_data]
            
            return df
        except Exception as e:
            print(f"Error creating visualization data: {e}")
            return None
    
    def generate_plotly_visualization(self, df, output_file=None):
        """
        Generate an interactive 3D visualization using Plotly
        """
        try:
            # Create a 3D scatter plot
            fig = px.scatter_3d(
                df,
                x='x',
                y='y',
                z='z',
                color='cluster',
                hover_name='filename',
                hover_data=['text_preview'],
                size_max=10,
                opacity=0.7,
                title='Vector Store Embeddings Visualization'
            )
            
            # Update layout for better visualization
            fig.update_layout(
                scene=dict(
                    xaxis=dict(showticklabels=False),
                    yaxis=dict(showticklabels=False),
                    zaxis=dict(showticklabels=False)
                ),
                margin=dict(l=0, r=0, b=0, t=30)
            )
            
            # Save to file if specified
            if output_file:
                fig.write_html(output_file)
                print(f"Visualization saved to {output_file}")
            
            return fig
        except Exception as e:
            print(f"Error generating visualization: {e}")
            return None
    
    def create_dash_app(self, df):
        """
        Create a Dash web application for interactive visualization
        """
        try:
            # Initialize the Dash app
            app = Dash(__name__)
            
            # Define the layout
            app.layout = html.Div([
                html.H1("OpenAI Vector Store Visualization"),
                
                # Filters and controls
                html.Div([
                    html.Label("Filter by Cluster:"),
                    dcc.Dropdown(
                        id='cluster-filter',
                        options=[{'label': f'Cluster {i}', 'value': i} for i in sorted(df['cluster'].unique())],
                        value=None,
                        multi=True
                    ),
                    
                    html.Label("Search Documents:"),
                    dcc.Input(
                        id='search-input',
                        type='text',
                        placeholder='Search by filename...'
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
                
                # 3D visualization
                dcc.Graph(id='3d-scatter', style={'height': '80vh'}),
                
                # Document details
                html.Div(id='document-details')
            ])
            
            # Define callbacks
            @app.callback(
                Output('3d-scatter', 'figure'),
                [Input('cluster-filter', 'value'),
                 Input('search-input', 'value')]
            )
            def update_graph(selected_clusters, search_term):
                filtered_df = df.copy()
                
                # Filter by cluster if selected
                if selected_clusters:
                    filtered_df = filtered_df[filtered_df['cluster'].isin(selected_clusters)]
                
                # Filter by search term if provided
                if search_term:
                    filtered_df = filtered_df[filtered_df['filename'].str.contains(search_term, case=False)]
                
                # Create the figure
                fig = px.scatter_3d(
                    filtered_df,
                    x='x',
                    y='y',
                    z='z',
                    color='cluster',
                    hover_name='filename',
                    hover_data=['text_preview'],
                    size_max=10,
                    opacity=0.7
                )
                
                # Update layout
                fig.update_layout(
                    scene=dict(
                        xaxis=dict(showticklabels=False),
                        yaxis=dict(showticklabels=False),
                        zaxis=dict(showticklabels=False)
                    ),
                    margin=dict(l=0, r=0, b=0, t=30)
                )
                
                return fig
            
            @app.callback(
                Output('document-details', 'children'),
                [Input('3d-scatter', 'clickData')]
            )
            def display_document_details(clickData):
                if not clickData:
                    return html.Div("Click on a point to see document details")
                
                # Get the index of the clicked point
                point_index = clickData['points'][0]['pointIndex']
                
                # Get the document details
                document = df.iloc[point_index]
                
                # Create the details display
                return html.Div([
                    html.H3(f"Document: {document['filename']}"),
                    html.P(f"Cluster: {document['cluster']}"),
                    html.P(f"ID: {document['id']}"),
                    html.H4("Text Preview:"),
                    html.P(document['text_preview']),
                    html.H4("Metadata:"),
                    html.Pre(json.dumps({k: v for k, v in document.items() if k not in ['x', 'y', 'z', 'cluster', 'id', 'filename', 'text_preview']}, indent=2))
                ])
            
            return app
        except Exception as e:
            print(f"Error creating Dash app: {e}")
            return None
    
    def visualize_vector_store(self, vector_store_id, max_results=1000, output_file=None, run_dash=False):
        """
        Main method to visualize a vector store
        """
        # Get vector store info
        store_info = self.get_vector_store_info(vector_store_id)
        print(f"Vector Store: {store_info.get('name', 'Unknown')} (ID: {store_info.get('id', 'Unknown')})")
        print(f"File Count: {store_info.get('file_count', 'Unknown')}")
        
        # Fetch embeddings
        print(f"Fetching up to {max_results} embeddings...")
        embeddings_data = self.fetch_embeddings(vector_store_id, max_results=max_results)
        
        if not embeddings_data:
            print("No embeddings found or error occurred.")
            return None
        
        print(f"Retrieved {len(embeddings_data)} embeddings.")
        
        # Extract embeddings as numpy array
        embeddings = np.array([data['embedding'] for data in embeddings_data])
        
        # Standardize the embeddings
        print("Standardizing embeddings...")
        scaler = StandardScaler()
        embeddings_scaled = scaler.fit_transform(embeddings)
        
        # Reduce dimensions
        print("Reducing dimensions with UMAP...")
        reduced_embeddings = self.reduce_dimensions(embeddings_scaled)
        
        if reduced_embeddings is None:
            print("Error reducing dimensions.")
            return None
        
        # Apply clustering
        print("Applying HDBSCAN clustering...")
        cluster_labels = self.apply_clustering(reduced_embeddings)
        
        if cluster_labels is None:
            print("Error applying clustering.")
            return None
        
        # Create visualization data
        print("Creating visualization data...")
        df = self.create_visualization_data(embeddings_data, reduced_embeddings, cluster_labels)
        
        if df is None:
            print("Error creating visualization data.")
            return None
        
        # Generate visualization
        print("Generating visualization...")
        fig = self.generate_plotly_visualization(df, output_file)
        
        if fig is None:
            print("Error generating visualization.")
            return None
        
        # Run Dash app if requested
        if run_dash:
            print("Starting Dash web application...")
            app = self.create_dash_app(df)
            if app:
                app.run_server(debug=True)
            else:
                print("Error creating Dash app.")
        
        return df

def main():
    parser = argparse.ArgumentParser(description="OpenAI Vector Store Visualizer")
    parser.add_argument("--store_id", required=True, help="Vector store ID")
    parser.add_argument("--api_key", help="OpenAI API Key (optional, can use OPENAI_API_KEY env var)")
    parser.add_argument("--max_results", type=int, default=1000, help="Maximum number of embeddings to retrieve")
    parser.add_argument("--output", help="Output HTML file path")
    parser.add_argument("--run_dash", action="store_true", help="Run Dash web application")
    parser.add_argument("--env_file", default=".env", help="Path to .env file (default: .env)")
    
    args = parser.parse_args()
    
    # Load from specific .env file if provided
    if args.env_file and args.env_file != ".env":
        load_dotenv(args.env_file)
    
    visualizer = VectorStoreVisualizer(api_key=args.api_key)
    visualizer.visualize_vector_store(
        vector_store_id=args.store_id,
        max_results=args.max_results,
        output_file=args.output,
        run_dash=args.run_dash
    )

if __name__ == "__main__":
    main()

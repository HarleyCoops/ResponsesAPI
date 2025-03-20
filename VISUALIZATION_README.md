# OpenAI Vector Store Visualization

This project provides tools to visualize OpenAI vector stores in 3D space. It allows you to explore the semantic relationships between your documents by visualizing their embeddings.

## Features

- Connect to OpenAI vector stores
- Retrieve embeddings from the vector store
- Perform dimensionality reduction using UMAP
- Apply clustering using HDBSCAN
- Generate interactive 3D visualizations using Plotly
- Explore document relationships through a web interface using Dash

## Prerequisites

- Python 3.8+
- OpenAI API key
- PDF documents to upload (optional)

## Installation

1. Ensure you have all the required dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```

## Usage

### Using the Interactive Scripts

For convenience, two interactive scripts are provided:

#### Windows Batch Script
```
run_visualization.bat
```

#### PowerShell Script
```
run_visualization.ps1
```

These scripts provide a menu-driven interface to:
1. Create a new vector store, upload PDFs, and visualize
2. Visualize an existing vector store

### Using the Command Line

#### Create a Vector Store and Visualize

```
python visualize_vector_store.py create-and-visualize --store_name "my_store" --pdf_dir "path/to/pdfs" --output "visualization.html"
```

#### Visualize an Existing Vector Store

```
python visualize_vector_store.py visualize --store_id "vs_your_vector_store_id" --output "visualization.html"
```

#### Run with Interactive Dash Web Application

Add the `--run_dash` flag to any command to launch an interactive web application:

```
python visualize_vector_store.py visualize --store_id "vs_your_vector_store_id" --run_dash
```

### Advanced Usage

For more advanced usage, you can use the Python modules directly:

```python
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
```

## Visualization Features

### Static HTML Visualization

The static HTML visualization provides:
- 3D scatter plot of document embeddings
- Color-coded clusters
- Hover information showing document details
- Interactive controls for zooming, rotating, and panning

### Dash Web Application

The Dash web application provides additional features:
- Filter by cluster
- Search for documents by filename
- Click on points to view detailed document information
- Interactive 3D navigation

## How It Works

1. **Data Retrieval**: The system connects to the OpenAI API and retrieves embeddings from the vector store.

2. **Dimensionality Reduction**: UMAP is used to reduce the high-dimensional embeddings (typically 1536 dimensions for OpenAI embeddings) to 3 dimensions for visualization.

3. **Clustering**: HDBSCAN is applied to identify semantic clusters in the reduced embedding space.

4. **Visualization**: The reduced embeddings are visualized in 3D space using Plotly, with points colored by cluster.

## Customization

You can customize the visualization by modifying the parameters in the `vector_store_visualizer.py` file:

- UMAP parameters (n_neighbors, min_dist, metric)
- HDBSCAN parameters (min_cluster_size, min_samples, cluster_selection_epsilon)
- Visualization settings (colors, point size, opacity)

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your OpenAI API key is correctly set in the `.env` file.

2. **No Embeddings Found**: Make sure your vector store contains documents and that the vector store ID is correct.

3. **Visualization Not Showing**: Check that you have the required dependencies installed and that the output file path is valid.

4. **Clustering Not Working Well**: Try adjusting the HDBSCAN parameters in the `apply_clustering` method.

### Getting Help

If you encounter issues, check the error messages for clues. Most errors will be related to API access, file paths, or missing dependencies.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

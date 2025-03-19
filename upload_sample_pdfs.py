import os
import argparse
import shutil
import requests
from tqdm import tqdm

# Sample PDF URLs from OpenAI's blog (these are examples, not real links)
SAMPLE_PDFS = [
    "https://example.com/pdf/openai_blog_1.pdf",
    "https://example.com/pdf/openai_blog_2.pdf",
    "https://example.com/pdf/openai_blog_3.pdf",
    # Add more sample PDFs here
]

def download_pdf(url, target_dir, filename=None):
    """
    Download a PDF from a URL and save to target directory
    """
    if filename is None:
        filename = os.path.basename(url)
    
    filepath = os.path.join(target_dir, filename)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        
        with open(filepath, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                size = f.write(data)
                bar.update(size)
                
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def copy_sample_pdf(source_path, target_dir):
    """
    Copy a sample PDF from local path to target directory
    """
    try:
        filename = os.path.basename(source_path)
        shutil.copy2(source_path, os.path.join(target_dir, filename))
        print(f"Copied {filename} to {target_dir}")
        return True
    except Exception as e:
        print(f"Error copying {source_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Upload sample PDFs to SearchOnThis directory")
    parser.add_argument("--target_dir", default="SearchOnThis", help="Target directory for PDFs")
    parser.add_argument("--source", choices=["download", "copy"], default="copy", 
                        help="Source of PDFs: download from URLs or copy from local path")
    parser.add_argument("--local_pdfs", nargs="+", help="Local PDF paths to copy (if source=copy)")
    
    args = parser.parse_args()
    
    # Ensure target directory exists
    if not os.path.exists(args.target_dir):
        os.makedirs(args.target_dir)
        print(f"Created directory: {args.target_dir}")
    
    if args.source == "download":
        print(f"Downloading {len(SAMPLE_PDFS)} sample PDFs to {args.target_dir}...")
        successful = 0
        for url in SAMPLE_PDFS:
            if download_pdf(url, args.target_dir):
                successful += 1
        print(f"Successfully downloaded {successful} of {len(SAMPLE_PDFS)} PDFs")
    
    elif args.source == "copy":
        if not args.local_pdfs:
            print("Error: No local PDFs specified. Use --local_pdfs to provide paths.")
            return
        
        print(f"Copying {len(args.local_pdfs)} PDFs to {args.target_dir}...")
        successful = 0
        for pdf_path in args.local_pdfs:
            if copy_sample_pdf(pdf_path, args.target_dir):
                successful += 1
        print(f"Successfully copied {successful} of {len(args.local_pdfs)} PDFs")
    
    print(f"Total PDFs in {args.target_dir}: {len(os.listdir(args.target_dir))}")

if __name__ == "__main__":
    main() 
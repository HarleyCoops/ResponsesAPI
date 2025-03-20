# OpenAI Vector Store Visualization PowerShell Script

Write-Host "OpenAI Vector Store Visualization" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python and try again." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found." -ForegroundColor Yellow
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Please edit the .env file to add your OpenAI API key." -ForegroundColor Yellow
        Write-Host "Press any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Host "Error: .env.example file not found." -ForegroundColor Red
        Write-Host "Please create a .env file with your OpenAI API key." -ForegroundColor Red
        exit 1
    }
}

# Check if requirements are installed
Write-Host "Checking and installing required packages..." -ForegroundColor Cyan
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "Choose an operation:" -ForegroundColor Cyan
Write-Host "1. Create a new vector store, upload PDFs, and visualize" -ForegroundColor White
Write-Host "2. Visualize an existing vector store" -ForegroundColor White
Write-Host "3. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Create a new vector store, upload PDFs, and visualize" -ForegroundColor Cyan
        Write-Host "===================================================" -ForegroundColor Cyan
        
        $storeName = Read-Host "Enter a name for the vector store"
        
        Write-Host ""
        $pdfDir = Read-Host "Enter the directory containing PDF files to upload"
        
        if (-not (Test-Path $pdfDir)) {
            Write-Host "Error: Directory does not exist." -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        $output = Read-Host "Enter the output HTML file path (leave empty for no output file)"
        
        $outputParam = ""
        if ($output -ne "") {
            $outputParam = "--output `"$output`""
        }
        
        Write-Host ""
        $runDashChoice = Read-Host "Run interactive Dash web application? (y/n)"
        $runDash = ""
        if ($runDashChoice -eq "y") {
            $runDash = "--run_dash"
        }
        
        Write-Host ""
        Write-Host "Running visualization..." -ForegroundColor Cyan
        Write-Host ""
        
        $command = "python visualize_vector_store.py create-and-visualize --store_name `"$storeName`" --pdf_dir `"$pdfDir`" $runDash $outputParam"
        Write-Host "Executing: $command" -ForegroundColor DarkGray
        Invoke-Expression $command
    }
    "2" {
        Write-Host ""
        Write-Host "Visualize an existing vector store" -ForegroundColor Cyan
        Write-Host "=================================" -ForegroundColor Cyan
        
        $storeId = Read-Host "Enter the vector store ID"
        
        Write-Host ""
        $output = Read-Host "Enter the output HTML file path (leave empty for no output file)"
        
        $outputParam = ""
        if ($output -ne "") {
            $outputParam = "--output `"$output`""
        }
        
        Write-Host ""
        $runDashChoice = Read-Host "Run interactive Dash web application? (y/n)"
        $runDash = ""
        if ($runDashChoice -eq "y") {
            $runDash = "--run_dash"
        }
        
        Write-Host ""
        Write-Host "Running visualization..." -ForegroundColor Cyan
        Write-Host ""
        
        $command = "python visualize_vector_store.py visualize --store_id `"$storeId`" $outputParam $runDash"
        Write-Host "Executing: $command" -ForegroundColor DarkGray
        Invoke-Expression $command
    }
    "3" {
        Write-Host "Exiting..." -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "Invalid choice." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""

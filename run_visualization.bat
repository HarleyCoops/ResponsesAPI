@echo off
setlocal enabledelayedexpansion

echo OpenAI Vector Store Visualization
echo ================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python and try again.
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found.
    echo Creating .env file from .env.example...
    
    if exist .env.example (
        copy .env.example .env
        echo Please edit the .env file to add your OpenAI API key.
        echo Press any key to continue...
        pause >nul
    ) else (
        echo Error: .env.example file not found.
        echo Please create a .env file with your OpenAI API key.
        exit /b 1
    )
)

REM Check if requirements are installed
echo Checking and installing required packages...
python -m pip install -r requirements.txt

echo.
echo Choose an operation:
echo 1. Create a new vector store, upload PDFs, and visualize
echo 2. Visualize an existing vector store
echo 3. Exit
echo.

set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" (
    echo.
    echo Create a new vector store, upload PDFs, and visualize
    echo ===================================================
    
    set /p store_name=Enter a name for the vector store: 
    
    echo.
    echo Enter the directory containing PDF files to upload:
    set /p pdf_dir=PDF directory: 
    
    if not exist "!pdf_dir!" (
        echo Error: Directory does not exist.
        exit /b 1
    )
    
    echo.
    echo Enter the output HTML file path (leave empty for no output file):
    set /p output=Output HTML file: 
    
    set run_dash=
    set /p run_dash_choice=Run interactive Dash web application? (y/n): 
    if /i "!run_dash_choice!"=="y" set run_dash=--run_dash
    
    echo.
    echo Running visualization...
    echo.
    
    python visualize_vector_store.py create-and-visualize --store_name "!store_name!" --pdf_dir "!pdf_dir!" !run_dash! !output!
    
) else if "%choice%"=="2" (
    echo.
    echo Visualize an existing vector store
    echo =================================
    
    set /p store_id=Enter the vector store ID: 
    
    echo.
    echo Enter the output HTML file path (leave empty for no output file):
    set /p output=Output HTML file: 
    
    set output_param=
    if not "!output!"=="" set output_param=--output "!output!"
    
    set run_dash=
    set /p run_dash_choice=Run interactive Dash web application? (y/n): 
    if /i "!run_dash_choice!"=="y" set run_dash=--run_dash
    
    echo.
    echo Running visualization...
    echo.
    
    python visualize_vector_store.py visualize --store_id "!store_id!" !output_param! !run_dash!
    
) else if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice.
    exit /b 1
)

echo.
echo Done.
echo.

endlocal

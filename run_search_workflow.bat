@echo off
echo OpenAI File Search Workflow
echo ===========================

echo Setting up environment...
set PDF_DIR=C:\Users\admin\ResponsesAPI\SearchOnThis
set OUTPUT_DIR=results

if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

echo.
echo Step 1: Creating vector store...
python search_api_implementation.py --action create_store --store_name "openai_blog_store" --output %OUTPUT_DIR%\store_details.json

echo.
echo Reading store ID from details file...
for /f "tokens=*" %%a in ('powershell -Command "Get-Content %OUTPUT_DIR%\store_details.json | ConvertFrom-Json | Select-Object -ExpandProperty id"') do set STORE_ID=%%a
echo Store ID: %STORE_ID%

echo.
echo Step 2: Uploading PDFs to vector store...
python search_api_implementation.py --action upload --store_id "%STORE_ID%" --pdf_dir "%PDF_DIR%" --output %OUTPUT_DIR%\upload_stats.json

echo.
echo Step 3: Generating evaluation questions...
python search_api_implementation.py --action generate_questions --pdf_dir "%PDF_DIR%" --output %OUTPUT_DIR%\questions.json

echo.
echo Step 4: Evaluating retrieval performance...
python search_api_implementation.py --action evaluate --store_id "%STORE_ID%" --output %OUTPUT_DIR%\questions.json --k 5

echo.
echo Step 5: Performing sample searches...
python search_api_implementation.py --action llm_search --store_id "%STORE_ID%" --query "What is Deep Research?"
echo.
python search_api_implementation.py --action llm_search --store_id "%STORE_ID%" --query "What are the main announcements from OpenAI in the last year?"

echo.
echo Workflow completed!
echo Results saved in: %OUTPUT_DIR% 
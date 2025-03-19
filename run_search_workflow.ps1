Write-Host "OpenAI File Search Workflow" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green

Write-Host "`nSetting up environment..." -ForegroundColor Cyan
$PDF_DIR = "C:\Users\admin\ResponsesAPI\SearchOnThis"
$OUTPUT_DIR = "results"

Write-Host "Note: Make sure your .env file contains a valid OPENAI_API_KEY" -ForegroundColor Yellow

if (-not (Test-Path $OUTPUT_DIR)) {
    New-Item -Path $OUTPUT_DIR -ItemType Directory | Out-Null
}

Write-Host "`nStep 1: Creating vector store..." -ForegroundColor Cyan
python search_api_implementation.py --action create_store --store_name "openai_blog_store" --output "$OUTPUT_DIR\store_details.json"

Write-Host "`nReading store ID from details file..." -ForegroundColor Cyan
$storeDetails = Get-Content "$OUTPUT_DIR\store_details.json" | ConvertFrom-Json
$STORE_ID = $storeDetails.id
Write-Host "Store ID: $STORE_ID" -ForegroundColor Yellow

# Save the store ID to .env file for future use
$envContent = Get-Content ".env"
$updatedContent = $envContent -replace "#?\s*VECTOR_STORE_ID=.*", "VECTOR_STORE_ID=$STORE_ID"
$updatedContent | Set-Content ".env"
Write-Host "Store ID saved to .env file" -ForegroundColor Green

Write-Host "`nStep 2: Uploading PDFs to vector store..." -ForegroundColor Cyan
python search_api_implementation.py --action upload --store_id "$STORE_ID" --pdf_dir "$PDF_DIR" --output "$OUTPUT_DIR\upload_stats.json"

Write-Host "`nStep 3: Generating evaluation questions..." -ForegroundColor Cyan
python search_api_implementation.py --action generate_questions --pdf_dir "$PDF_DIR" --output "$OUTPUT_DIR\questions.json"

Write-Host "`nStep 4: Evaluating retrieval performance..." -ForegroundColor Cyan
python search_api_implementation.py --action evaluate --store_id "$STORE_ID" --output "$OUTPUT_DIR\questions.json" --k 5

Write-Host "`nStep 5: Performing sample searches..." -ForegroundColor Cyan
Write-Host "`nSample Query 1: What is Deep Research?" -ForegroundColor Yellow
python search_api_implementation.py --action llm_search --store_id "$STORE_ID" --query "What is Deep Research?"

Write-Host "`nSample Query 2: What are the main announcements from OpenAI in the last year?" -ForegroundColor Yellow
python search_api_implementation.py --action llm_search --store_id "$STORE_ID" --query "What are the main announcements from OpenAI in the last year?"

Write-Host "`nWorkflow completed!" -ForegroundColor Green
Write-Host "Results saved in: $OUTPUT_DIR" -ForegroundColor Green 
import unittest
import os
import json
from unittest.mock import patch, MagicMock
from search_api_implementation import OpenAIFileSearch

class TestOpenAIFileSearch(unittest.TestCase):
    
    def setUp(self):
        # Set up test environment
        os.environ["OPENAI_API_KEY"] = "fake-api-key-for-testing"
        self.search_api = OpenAIFileSearch()
        self.test_vector_store_id = "vs_test123456"
        self.test_pdf_dir = "test_pdfs"
        
        # Create test directory if it doesn't exist
        if not os.path.exists(self.test_pdf_dir):
            os.makedirs(self.test_pdf_dir)
    
    @patch('search_api_implementation.OpenAI')
    def test_create_vector_store(self, mock_openai):
        # Mock the OpenAI client's response
        mock_client = MagicMock()
        mock_vector_store = MagicMock()
        mock_vector_store.id = "vs_test123456"
        mock_vector_store.name = "test_store"
        mock_vector_store.created_at = 1234567890
        mock_vector_store.file_counts.completed = 0
        
        mock_client.vector_stores.create.return_value = mock_vector_store
        mock_openai.return_value = mock_client
        
        # Replace the real client with our mock
        self.search_api.client = mock_client
        
        # Test the method
        result = self.search_api.create_vector_store("test_store")
        
        # Verify the result
        self.assertEqual(result["id"], "vs_test123456")
        self.assertEqual(result["name"], "test_store")
        self.assertEqual(result["created_at"], 1234567890)
        self.assertEqual(result["file_count"], 0)
        
        # Verify that the method called the right API
        mock_client.vector_stores.create.assert_called_once_with(name="test_store")
    
    @patch('search_api_implementation.OpenAI')
    def test_upload_single_pdf(self, mock_openai):
        # Create a test PDF file
        test_pdf_path = os.path.join(self.test_pdf_dir, "test.pdf")
        with open(test_pdf_path, 'w') as f:
            f.write("Test PDF content")
        
        # Mock the OpenAI client's response
        mock_client = MagicMock()
        mock_file_response = MagicMock()
        mock_file_response.id = "file_test123456"
        
        mock_client.files.create.return_value = mock_file_response
        mock_openai.return_value = mock_client
        
        # Replace the real client with our mock
        self.search_api.client = mock_client
        
        # Test the method
        result = self.search_api.upload_single_pdf(test_pdf_path, self.test_vector_store_id)
        
        # Verify the result
        self.assertEqual(result["file"], "test.pdf")
        self.assertEqual(result["status"], "success")
        
        # Verify that the method called the right APIs
        mock_client.files.create.assert_called_once()
        mock_client.vector_stores.files.create.assert_called_once_with(
            vector_store_id=self.test_vector_store_id,
            file_id="file_test123456"
        )
        
        # Clean up
        os.remove(test_pdf_path)
    
    @patch('search_api_implementation.OpenAI')
    def test_vector_search(self, mock_openai):
        # Mock the OpenAI client's response
        mock_client = MagicMock()
        mock_search_result = MagicMock()
        mock_result_data = MagicMock()
        mock_result_data.filename = "test.pdf"
        mock_result_data.score = 0.95
        mock_content = MagicMock()
        mock_content.text = "Test content"
        mock_result_data.content = [mock_content]
        mock_search_result.data = [mock_result_data]
        
        mock_client.vector_stores.search.return_value = mock_search_result
        mock_openai.return_value = mock_client
        
        # Replace the real client with our mock
        self.search_api.client = mock_client
        
        # Test the method
        result = self.search_api.vector_search(self.test_vector_store_id, "test query")
        
        # Verify the result
        self.assertEqual(result.data[0].filename, "test.pdf")
        self.assertEqual(result.data[0].score, 0.95)
        self.assertEqual(result.data[0].content[0].text, "Test content")
        
        # Verify that the method called the right API
        mock_client.vector_stores.search.assert_called_once_with(
            vector_store_id=self.test_vector_store_id,
            query="test query"
        )
    
    @patch('search_api_implementation.OpenAI')
    def test_llm_integrated_search(self, mock_openai):
        # Mock the OpenAI client's response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_output = [MagicMock(), MagicMock()]
        mock_content = MagicMock()
        mock_annotation = MagicMock()
        mock_annotation.filename = "test.pdf"
        mock_content.annotations = [mock_annotation]
        mock_content.text = "LLM generated response"
        mock_output[1].content = [mock_content]
        mock_response.output = mock_output
        
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Replace the real client with our mock
        self.search_api.client = mock_client
        
        # Test the method
        result = self.search_api.llm_integrated_search(self.test_vector_store_id, "test query")
        
        # Verify the result
        self.assertEqual(result["files_used"], ["test.pdf"])
        self.assertEqual(result["response"], "LLM generated response")
        
        # Verify that the method called the right API
        mock_client.responses.create.assert_called_once()
    
    def tearDown(self):
        # Clean up test environment
        if os.path.exists(self.test_pdf_dir):
            os.rmdir(self.test_pdf_dir)

if __name__ == '__main__':
    unittest.main() 
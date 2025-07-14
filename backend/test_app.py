#!/usr/bin/env python3
"""
Test suite for Ren voice assistant backend.
"""

import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from agent import Agent
from config import Config

class TestRenBackend(unittest.TestCase):
    """Test cases for Ren backend functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('agent_initialized', data)
        self.assertIn('voice_enabled', data)
    
    def test_config_endpoint(self):
        """Test configuration endpoint."""
        response = self.app.get('/config')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('agent_name', data)
        self.assertIn('whisper_model', data)
        self.assertIn('voice_enabled', data)
    
    def test_text_endpoint_valid_input(self):
        """Test text endpoint with valid input."""
        payload = {"message": "Hello, Ren!"}
        response = self.app.post('/ask', 
                                json=payload,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn('conversation_summary', data)
    
    def test_text_endpoint_empty_message(self):
        """Test text endpoint with empty message."""
        payload = {"message": ""}
        response = self.app.post('/ask',
                                json=payload,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_text_endpoint_missing_message(self):
        """Test text endpoint with missing message field."""
        payload = {"not_message": "Hello"}
        response = self.app.post('/ask',
                                json=payload,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_text_endpoint_invalid_json(self):
        """Test text endpoint with invalid JSON."""
        response = self.app.post('/ask',
                                data="invalid json",
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_404_handler(self):
        """Test 404 error handler."""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)

class TestAgent(unittest.TestCase):
    """Test cases for Agent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = Agent()
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertIsInstance(self.agent.conversation_memory, list)
        self.assertIn('name', self.agent.traits)
        self.assertIn('personality', self.agent.traits)
        self.assertIn('memory_threshold', self.agent.traits)
    
    def test_process_statement_valid_input(self):
        """Test processing valid input."""
        response = self.agent.process_statement("Hello")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    
    def test_process_statement_empty_input(self):
        """Test processing empty input."""
        with self.assertRaises(ValueError):
            self.agent.process_statement("")
    
    def test_process_statement_none_input(self):
        """Test processing None input."""
        with self.assertRaises(ValueError):
            self.agent.process_statement(None)
    
    def test_process_statement_non_string_input(self):
        """Test processing non-string input."""
        with self.assertRaises(ValueError):
            self.agent.process_statement(123)
    
    def test_memory_management(self):
        """Test conversation memory management."""
        # Fill memory beyond threshold
        for i in range(5):
            self.agent.process_statement(f"Message {i}")
        
        # Check memory doesn't exceed threshold
        self.assertLessEqual(len(self.agent.conversation_memory), 
                           self.agent.traits['memory_threshold'])
    
    def test_conversation_summary(self):
        """Test conversation summary generation."""
        self.agent.process_statement("Hello")
        summary = self.agent.get_conversation_summary()
        
        self.assertIn('memory_count', summary)
        self.assertIn('memory_threshold', summary)
        self.assertIn('recent_inputs', summary)
        self.assertIn('agent_name', summary)
        self.assertIn('personality', summary)

class TestConfig(unittest.TestCase):
    """Test cases for Config class."""
    
    def test_config_initialization(self):
        """Test config initialization."""
        config = Config()
        self.assertIsNotNone(config.WHISPER_MODEL)
        self.assertIsNotNone(config.AUDIO_SAMPLE_RATE)
        self.assertIsNotNone(config.AGENT_NAME)
    
    def test_validate_required_config(self):
        """Test configuration validation."""
        config = Config()
        missing = config.validate_required_config()
        self.assertIsInstance(missing, list)
    
    @patch.dict(os.environ, {'ELEVENLABS_API_KEY': 'test_key', 'ELEVEN_VOICE_ID': 'test_voice'})
    def test_voice_enabled_with_config(self):
        """Test voice enabled when properly configured."""
        config = Config()
        config.load_environment()
        self.assertTrue(config.is_voice_enabled())
    
    def test_voice_disabled_without_config(self):
        """Test voice disabled when not configured."""
        config = Config()
        # Clear any existing env vars
        config.ELEVENLABS_API_KEY = None
        config.ELEVEN_VOICE_ID = None
        self.assertFalse(config.is_voice_enabled())

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)

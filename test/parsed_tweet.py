import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.classes import ParsedTweet

class MockTweet:
    def __init__(self, media=None):
        self.media = media or []

class TestParsedTweet(unittest.TestCase):
    def setUp(self):
        # Intercept and simulate the translation function t() to prevent a missing key error from being thrown
        self.patcher = patch('core.classes.t', side_effect=lambda key, **kwargs: f"Mock({key})")
        self.mock_t = self.patcher.start()
        
        # Create a basic ParsedTweet instance using a dict
        self.source_dict = {
            'tweet': {
                'raw_text': {'text': None},
                'author': {'screen_name': 'test_user'},
                'media': {'all': []},
                'translation': {'text': None, 'source_lang': 'en'}
            }
        }
        self.parsed_tweet = ParsedTweet(self.source_dict)
        
    def tearDown(self):
        # Stop interception after the test ends
        self.patcher.stop()

    def test_get_text_priority(self):
        """Test that get_text prioritizes translated text over raw text."""
        self.parsed_tweet.text = "Original Text"
        self.parsed_tweet.trans_text = "Translated Text"
        self.parsed_tweet.trans_lang = "en"
        
        # Should return translated text (which is a formatted string in get_translated_text)
        result, is_simplified = self.parsed_tweet.get_text()
        self.assertIn("Translated Text", result)
        # Confirmed call to Mock translation
        self.assertIn("Mock(class.parsed_tweet.trans_text)", result) 
        self.assertFalse(is_simplified)
        
        # Should return original text if translation is missing
        self.parsed_tweet.trans_text = None
        result, is_simplified = self.parsed_tweet.get_text()
        self.assertEqual(result, "Original Text")
        self.assertFalse(is_simplified)

    def test_get_text_none(self):
        """Test get_text when both text and trans_text are None."""
        self.parsed_tweet.text = None
        self.parsed_tweet.trans_text = None
        self.assertIsNone(self.parsed_tweet.get_text())

    def test_simplified_content_threshold(self):
        """Test that _simplified_content correctly identifies content over threshold."""
        # SIMPLIFIED_THRESHOLD is 400
        # MAX_DESCRIPTION_LENGTH is 650
        # To trigger truncation, we need text visible length > 650
        short_text = "A" * 100
        long_text = "A" * 700
        
        # Short text should not be simplified
        result, is_simplified = self.parsed_tweet._simplified_content(short_text)
        self.assertEqual(result, short_text)
        self.assertFalse(is_simplified)
        
        # Long text should be simplified (is_simplified becomes True if > 400)
        result, is_simplified = self.parsed_tweet._simplified_content(long_text)
        self.assertTrue(is_simplified)
        self.assertTrue(len(result) < len(long_text))
        self.assertTrue(result.endswith("..."))

    def test_get_text_simplified(self):
        """Test get_text with simplified_content=True."""
        long_text = "A" * 700
        self.parsed_tweet.text = long_text
        
        result, is_simplified = self.parsed_tweet.get_text(simplified_content=True)
        self.assertTrue(is_simplified)
        self.assertTrue(len(result) < 700)

    def test_get_quote_text_repro(self):
        """Test get_quote_text with the new simplified logic."""
        self.parsed_tweet.quote.text = "Quote Content"
        self.parsed_tweet.text = "Main Content"
        
        # Test with main text included
        result = self.parsed_tweet.get_quote_text(include_main_text=True)
        # result should be (content, is_simplified)
        self.assertIsInstance(result, tuple)
        content, _ = result
        self.assertIn("Main Content", content)
        self.assertIn("> Quote Content", content)
        self.assertNotIn("('Main Content', False)", content)

if __name__ == '__main__':
    unittest.main()

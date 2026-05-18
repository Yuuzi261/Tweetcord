import os
import sys
import unittest

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import clean_markdown, get_visible_length, safe_truncate

class TestMarkdownUtils(unittest.TestCase):
    
    def test_clean_markdown(self):
        """Test that Markdown syntax is correctly stripped to reveal visible text."""
        test_cases = [
            ("**Bold**", "Bold"),
            ("__Underline__", "Underline"),
            ("***Bold Italic***", "Bold Italic"),
            ("~~Strikethrough~~", "Strikethrough"),
            ("||Spoiler||", "Spoiler"),
            ("`Code`", "Code"),
            ("```Code Block```", "Code Block"),
            ("[Link Text](https://example.com)", "Link Text"),
            ("> Quote line", "Quote line"),
            ("> Multiple\n> Quotes", "Multiple\nQuotes"),
            ("Normal text with **Bold** and [Link](url)", "Normal text with Bold and Link"),
            ("___***Nested***___", "Nested"),
        ]
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(clean_markdown(input_text), expected)

    def test_get_visible_length(self):
        """Test that character count only includes visible characters."""
        self.assertEqual(get_visible_length("**12345**"), 5)
        self.assertEqual(get_visible_length("[123](url)"), 3)
        self.assertEqual(get_visible_length("> 12345"), 5)
        self.assertEqual(get_visible_length("12\n34"), 5)  # \n counts as 1

    def test_safe_truncate_simple(self):
        """Test truncation of plain text."""
        res, truncated = safe_truncate("Hello World", 8)
        self.assertEqual(res, "Hello...")
        self.assertTrue(truncated)

        res, truncated = safe_truncate("Short", 10)
        self.assertEqual(res, "Short")
        self.assertFalse(truncated)

    def test_safe_truncate_bold(self):
        """Test that bold tags are preserved and closed after truncation."""
        # Visible: "Bold Content" (12). Limit: 10. Max visible allowed: 7.
        # "Bold Co" (7) -> "**Bold Co...**"
        res, truncated = safe_truncate("**Bold Content**", 10)
        self.assertEqual(res, "**Bold Co...**")
        self.assertTrue(truncated)

    def test_safe_truncate_links(self):
        """Test that links are truncated inside the display text and remain valid."""
        # Visible: "Detailed Link" (13). Limit: 10. Max visible: 7.
        # "Detaile" (7) -> "[Detaile...](url)"
        res, truncated = safe_truncate("[Detailed Link](https://example.com)", 10)
        self.assertEqual(res, "[Detaile...](https://example.com)")
        self.assertTrue(truncated)

    def test_safe_truncate_nested(self):
        """Test nested tags are correctly closed in the right order."""
        # Visible: "Nested Text" (11). Limit: 10. Max visible: 7.
        # "Nested " (7) -> "___**Nested ...**___"
        res, truncated = safe_truncate("___**Nested Text**___", 10)
        self.assertEqual(res, "___**Nested ...**___")
        self.assertTrue(truncated)

    def test_safe_truncate_quotes(self):
        """Test that quote prefixes are preserved across newlines."""
        text = "> Line 1\n> Line 2\n> Line 3"
        # Visible: "Line 1\nLine 2\nLine 3" (20)
        # Limit 12. Max visible 9.
        # "Line 1\nLi" (9)
        res, truncated = safe_truncate(text, 12)
        self.assertTrue(truncated)
        self.assertIn("> Line 1", res)
        self.assertIn("> Li...", res)

    def test_safe_truncate_code(self):
        """Test that inline code blocks are handled correctly."""
        res, truncated = safe_truncate("`Code content here`", 10)
        # Visible: "Code content here" (17). Max visible: 7.
        # "`Code co...`"
        self.assertEqual(res, "`Code co...`")
        self.assertTrue(truncated)

    def test_safe_truncate_spoiler(self):
        """Test that spoilers are closed after truncation."""
        res, truncated = safe_truncate("||Hidden secret message||", 15)
        # Visible: "Hidden secret message" (21). Max visible: 12.
        # "||Hidden secre...||"
        self.assertEqual(res, "||Hidden secre...||")
        self.assertTrue(truncated)

    def test_safe_truncate_midword_underscore(self):
        """Test that underscores in the middle of words are not treated as tags."""
        # "Blue_ArchiveJP" should not be truncated into "Blue_Ar..._"
        res, truncated = safe_truncate("Blue_ArchiveJP", 10)
        # Visible: 14. Limit: 7.
        # "Blue_Ar..."
        self.assertEqual(res, "Blue_Ar...")
        self.assertTrue(truncated)
        self.assertFalse(res.endswith("_"))
        
    def test_safe_truncate_link_with_parentheses(self):
        """Test URLs with parentheses are handled correctly."""
        text = "[Wikipedia](https://en.wikipedia.org/wiki/File_(command))"
        res, truncated = safe_truncate(text, 50)
        self.assertEqual(res, text)

if __name__ == '__main__':
    unittest.main()

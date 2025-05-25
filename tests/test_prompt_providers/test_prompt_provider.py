import unittest

# Assuming the PromptProvider class is in src/prompt_providers/prompt_provider.py
from src.prompt_providers.prompt_provider import PromptProvider

class TestPromptProvider(unittest.TestCase):

    def test_get_prompt_not_implemented(self):
        provider = PromptProvider()
        with self.assertRaises(NotImplementedError) as cm:
            provider.get_prompt("some_input")
        self.assertEqual(str(cm.exception), "Subclasses must implement this method.")

if __name__ == '__main__':
    unittest.main()

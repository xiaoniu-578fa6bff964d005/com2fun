import unittest
import os
import dotenv

dotenv.load_dotenv()

import openai
import anthropic
import com2fun


class BasicTestCase(unittest.TestCase):
    def test_openai_chat(self):
        @com2fun.com2fun
        def top(category: str, n) -> list[str]:
            """top n items"""

        top.add_example("continents", 3)(["Asia", "Africa", "North America"])
        r = top("fish", 5)
        self.assertTrue(isinstance(r, list))

    def test_openai_completion(self):
        @com2fun.com2fun(
            SF=com2fun.SF.openai.OpenAICompletionSF,
            composer=com2fun.DefaultCompletionComposer(),
            client=openai.AzureOpenAI(
                base_url=os.getenv("AZURE_TEXT_DAVINCI_003_ENDPOINT"),
                api_key=os.getenv("AZURE_TEXT_DAVINCI_003_KEY"),
                api_version="2023-05-15",
            ),
        )
        def top(category: str, n) -> list[str]:
            """top n items"""

        top.add_example("continents", 3)(["Asia", "Africa", "North America"])
        r = top("fish", 5)
        self.assertTrue(isinstance(r, list))

    def test_anthropic_chat(self):
        @com2fun.com2fun(
            SF=com2fun.SF.anthropic.AnthropicChatSF, client=anthropic.Anthropic()
        )
        def top(category: str, n) -> list[str]:
            """top n items"""

        top.add_example("continents", 3)(["Asia", "Africa", "North America"])
        r = top("fish", 5)
        self.assertTrue(isinstance(r, list))

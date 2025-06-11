from ...base.agent_base import AgentBase
from .models import SentimentModel
from .prompts import ANALYZE_SENTIMENT


class SentimentAgent(AgentBase):
    """Agent specialized in analyzing the sentiment of a given text."""

    async def analyze(self, text_to_analyze: str, **kwargs) -> SentimentModel:
        """
        Analyzes the sentiment of a piece of text.

        Args:
            text_to_analyze: The text to be analyzed.

        Returns:
            A SentimentModel object containing the analysis.
        """

        full_prompt = f"{ANALYZE_SENTIMENT}\n\n--- TEXT TO ANALYZE ---\n{text_to_analyze}"

        result = await self.run(
            prompt=full_prompt,
            pydantic_model=SentimentModel,
            **kwargs
        )

        return result

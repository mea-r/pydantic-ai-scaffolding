"""Feedback agent implementation"""
from ...base.agent_base import AgentBase
from .models import EditingFeedback
from .prompts import PROVIDE_FEEDBACK


class FeedbackAgent(AgentBase):
    """Agent specialized in providing editorial feedback and quality assessment"""

    async def provide_feedback(self, original_content: str, edited_content: str,
                               **kwargs) -> EditingFeedback:
        """Compare original and edited content, provide detailed feedback"""
        
        prompt = PROVIDE_FEEDBACK.format(
            original_content=original_content,
            edited_content=edited_content
        )
        
        result = await self.run(
            prompt=prompt,
            pydantic_model=EditingFeedback,
            **kwargs
        )
        
        return result
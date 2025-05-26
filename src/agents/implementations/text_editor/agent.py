"""Text editor agent implementation"""
from ...base.agent_base import AgentBase
from .models import EditedContent
from .prompts import EDIT_CONTENT, APPLY_FEEDBACK


class TextEditorAgent(AgentBase):
    """Agent specialized in text editing and improvement"""

    async def edit_content(self, content: str, **kwargs) -> EditedContent:
        """Edit and improve the provided content"""
        
        prompt = EDIT_CONTENT.format(content=content)
        result = await self.run(
            prompt=prompt,
            pydantic_model=EditedContent,
            **kwargs
        )
        
        return result

    async def apply_feedback(self, original_content: str, edited_content: str,
                             feedback: str, **kwargs) -> EditedContent:
        """Apply feedback to improve the edited content"""
        
        prompt = APPLY_FEEDBACK.format(
            original_content=original_content,
            edited_content=edited_content,
            feedback=feedback
        )
        
        result = await self.run(
            prompt=prompt,
            pydantic_model=EditedContent,
            **kwargs
        )
        
        return result
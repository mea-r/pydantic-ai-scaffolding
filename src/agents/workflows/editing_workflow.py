"""Content editing workflow implementation"""
import asyncio
from typing import Union, Dict, Any, Optional
from pathlib import Path

from .base_workflow import BaseWorkflow


class ContentEditingWorkflow(BaseWorkflow):
    """Orchestrates the multi-agent editing workflow"""

    def __init__(self, ai_helper):
        super().__init__(ai_helper, "content_editing")
        self._initialize_agents()

    async def execute(self, file_path: Union[str, Path], max_iterations: Optional[int] = None) -> Dict[str, Any]:
        """
        Complete content editing workflow:
        1. Process file content
        2. Edit the content
        3. Get feedback on the edit
        4. Apply feedback to improve the edit
        """
        
        max_iterations = max_iterations or self.get_config_value('max_iterations', 2)
        quality_threshold = self.get_config_value('quality_threshold', 0.85)

        print("🔄 Starting content editing workflow...")

        # Step 1: Process the file
        print("📄 Step 1: Processing file content...")
        file_processor = self.agents['file_processor']
        processed_content = await file_processor.process_file(file_path)
        print(f"✅ File processed. Content length: {len(processed_content.extracted_text)} chars")

        # Step 2: Initial edit
        print("✏️  Step 2: Initial content editing...")
        text_editor = self.agents['text_editor']
        edited_content = await text_editor.edit_content(processed_content.extracted_text)
        print(f"✅ Initial edit complete. {len(edited_content.changes_made)} changes made")

        current_edit = edited_content
        final_feedback = None

        # Step 3 & 4: Feedback loop
        feedback_agent = self.agents['feedback']
        
        for iteration in range(max_iterations):
            print(f"🔍 Step {3 + iteration}: Getting feedback (iteration {iteration + 1})...")

            feedback = await feedback_agent.provide_feedback(
                processed_content.extracted_text,
                current_edit.edited_text
            )

            print(f"📊 Feedback received. Quality score: {feedback.quality_score:.2f}")
            final_feedback = feedback

            # If quality is high enough, we might stop early
            if feedback.quality_score > quality_threshold and iteration > 0:
                print("🎯 High quality achieved, stopping iterations")
                break

            # Don't apply feedback on the last iteration if we're not stopping early
            if iteration < max_iterations - 1:
                print(f"🔄 Applying feedback (iteration {iteration + 1})...")
                
                feedback_text = (
                    f"Overall: {feedback.overall_assessment}\n"
                    f"Specific feedback: {'; '.join(feedback.specific_feedback)}\n"
                    f"Suggestions: {'; '.join(feedback.suggestions)}"
                )
                
                current_edit = await text_editor.apply_feedback(
                    processed_content.extracted_text,
                    current_edit.edited_text,
                    feedback_text
                )

                print(f"✅ Feedback applied. Confidence: {current_edit.confidence_score:.2f}")

        print("\n" + "=" * 50)
        print("WORKFLOW COMPLETE")
        print("=" * 50)

        return {
            'original_content': processed_content,
            'final_edit': current_edit,
            'final_feedback': final_feedback,
            'workflow_config': self.config
        }

    async def run_and_display(self, file_path: Union[str, Path], **kwargs):
        """Convenience method to run workflow and display results"""
        result = await self.execute(file_path, **kwargs)
        
        print(f"Original summary: {result['original_content'].summary}")
        print(f"Final edit confidence: {result['final_edit'].confidence_score:.2f}")
        if result['final_feedback']:
            print(f"Final quality score: {result['final_feedback'].quality_score:.2f}")
        print("\nFinal edited content:")
        print("-" * 30)
        print(result['final_edit'].edited_text)
        
        return result

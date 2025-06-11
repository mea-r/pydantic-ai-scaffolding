"""Content editing workflow implementation"""
from typing import Union, Dict, Any, Optional
from pathlib import Path

from .base_workflow import BaseWorkflow


class SentimentWorkflow(BaseWorkflow):
    """Orchestrates the multi-agent editing workflow"""

    def __init__(self, ai_helper):
        super().__init__(ai_helper, "sentiment_aware_editing")
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

        try:
            print("🔄 Starting content editing workflow...")

            processed_content = await self._execute_stage('file_processing', 'file_processor', 'process_file',
                                                          file_path)
            print(f"✅ File processed. Content length: {len(processed_content.extracted_text)} chars")

            current_edit = await self._execute_stage('initial_editing', 'text_editor', 'edit_content',
                                                     processed_content.extracted_text)
            print(f"✅ Initial edit complete. {len(current_edit.changes_made)} changes made")

            final_feedback = None

            feedback_agent = self.agents['feedback']

            for iteration in range(max_iterations):
                print(f"🔍 Step {3 + iteration}: Getting feedback (iteration {iteration + 1})...")

                feedback = await feedback_agent.provide_feedback(
                    processed_content.extracted_text,
                    current_edit.edited_text
                )

                print(f"📊 Feedback received. Quality score: {feedback.quality_score:.2f}")
                final_feedback = feedback

                if feedback.quality_score > quality_threshold and iteration > 0:
                    print("🎯 High quality achieved, stopping iterations")
                    break

                if iteration < max_iterations - 1:
                    print(f"🔄 Applying feedback (iteration {iteration + 1})...")

                    feedback_text = (
                        f"Overall: {feedback.overall_assessment}\n"
                        f"Specific feedback: {'; '.join(feedback.specific_feedback)}\n"
                        f"Suggestions: {'; '.join(feedback.suggestions)}"
                    )

                    current_edit = await self.agents['text_editor'].apply_feedback(
                        processed_content.extracted_text,
                        current_edit.edited_text,
                        feedback_text
                    )

                    print(f"✅ Feedback applied. Confidence: {current_edit.confidence_score:.2f}")

            sentiment_result = None
            if 'sentiment' in self.agents:
                final_text_to_analyze = current_edit.edited_text
                sentiment_result = await self._execute_stage(
                    'sentiment_analysis',
                    'sentiment',
                    'analyze',
                    final_text_to_analyze
                )
                print(f"✅ Sentiment analysis complete. Result: {sentiment_result.sentiment.value}")

            print("\n" + "=" * 50)
            print("WORKFLOW COMPLETE")
            print("=" * 50)

            return {
                'original_content': processed_content,
                'final_edit': current_edit,
                'final_feedback': final_feedback,
                'sentiment_result': sentiment_result,
                'processing_report': self._generate_report(),
                'success': True
            }

        except Exception as e:
            error_msg = f"Content editing workflow failed: {str(e)}"
            self.processing_report['errors'].append(error_msg)
            self._log(error_msg, level='error')

            return {
                'original_content': None,
                'final_edit': None,
                'final_feedback': None,
                'processing_report': self._generate_report(),
                'success': False,
                'error': str(e)
            }

    async def validate_prerequisites(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Validate that all prerequisites are met for workflow execution"""
        validation_result = await super().validate_prerequisites(**kwargs)

        if not Path(file_path).exists():
            validation_result['valid'] = False
            validation_result['errors'].append(f"File not found: {file_path}")

        return validation_result

    async def run_and_display(self, file_path: Union[str, Path], **kwargs):
        """Convenience method to run workflow and display results"""
        result = await self.execute(file_path, **kwargs)

        if result['success']:
            print(f"Original summary: {result['original_content'].summary}")
            print(f"Final edit confidence: {result['final_edit'].confidence_score:.2f}")

            if result.get('final_feedback'):
                print(f"Final quality score: {result['final_feedback'].quality_score:.2f}")

            if result.get('sentiment_result'):
                sentiment = result['sentiment_result'].sentiment.value
                score = result['sentiment_result'].confidence_score
                print(f"Sentiment Analysis: {sentiment} (Score: {score:.2f})")

            print("\nFinal edited content:")
            print("-" * 30)
            print(result['final_edit'].edited_text)
        else:
            print(f"Workflow failed: {result.get('error', 'Unknown error')}")

        return result

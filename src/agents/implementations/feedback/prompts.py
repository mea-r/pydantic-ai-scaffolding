"""Prompts for feedback agent"""

PROVIDE_FEEDBACK = """
Compare the original content with the edited version and provide comprehensive feedback.

ORIGINAL CONTENT:
{original_content}

EDITED CONTENT:
{edited_content}

Please provide:
1. Overall assessment of the editing quality
2. Specific feedback on what was done well
3. Specific feedback on what could be improved
4. Suggestions for further improvement
5. Quality score (0-1 scale) for the editing work
6. Key areas that need attention

Consider:
- Did the edit improve clarity and readability?
- Was the original meaning preserved?
- Are there any errors introduced?
- Could further improvements be made?
- Is the tone and style appropriate?
"""
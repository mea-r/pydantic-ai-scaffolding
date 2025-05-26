"""Prompts for text editor agent"""

EDIT_CONTENT = """
Please edit and improve the following text:

ORIGINAL TEXT:
{content}

Your tasks:
1. Correct grammar, spelling, and punctuation errors
2. Improve clarity and readability
3. Enhance flow and organization
4. Maintain the original meaning and tone
5. Provide a list of changes made
6. Explain your editing rationale
7. Rate your confidence in the improvements (0-1 scale)

Focus on meaningful improvements rather than superficial changes.
"""

APPLY_FEEDBACK = """
You previously edited some content, and now you've received feedback. 
Please revise your work based on this feedback.

ORIGINAL CONTENT:
{original_content}

YOUR PREVIOUS EDIT:
{edited_content}

FEEDBACK RECEIVED:
{feedback}

Please:
1. Consider the feedback carefully
2. Revise your edited content accordingly
3. Explain what changes you made based on the feedback
4. Provide your confidence score for this revision
"""
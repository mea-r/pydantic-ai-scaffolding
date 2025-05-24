
class PromptProvider:
    """
    Base class for all prompt providers. This class defines the interface that all prompt providers must implement.
    """

    def __init__(self):
        pass

    def get_prompt(self, *args, **kwargs) -> str:
        """
        Get the prompt string. This method should be implemented by all subclasses.

        Returns:
            str: The prompt string.
        """
        raise NotImplementedError("Subclasses must implement this method.")

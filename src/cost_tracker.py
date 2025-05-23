


class CostTracker:
    def __init__(self):
        self._total_cost = 0

        # maintained in three files (main level):
        # py_model_cost.json
        # llm_model_cost.json
        # total_cost.json

        self._cost_info = {}
        self._init_cost_info()

    def track_cost(self, cost_details):
        # Logic to track cost based on details (e.g., model, tokens, price)
        pass

    def get_total_cost(self):
        return self._total_cost

    def reset_cost(self):
        self._total_cost = 0

    # Example method to add cost (could be based on tokens, etc.)
    def add_cost(self, input_tokens:int, output_tokens: int, pydantic_model: str, llm_model: str):
        # calculate cost using input and output tokens

        # add cost per pydantic_model
        # add cost per llm_model
        # add cost per total

        pass

    """
    1) pull cost information from https://openrouter.ai/api/v1/models (no auth required)
    2) save and cache for 1 day. models.json
    """
    def _init_cost_info(self):
        pass

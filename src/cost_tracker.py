class CostTracker:
    def __init__(self):
        self._total_cost = 0

    def track_cost(self, cost_details):
        # Logic to track cost based on details (e.g., model, tokens, price)
        pass

    def get_total_cost(self):
        return self._total_cost

    def reset_cost(self):
        self._total_cost = 0

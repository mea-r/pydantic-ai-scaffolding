from src.adapters.base_adapter import BaseAdapter

class DeepSeekAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        self.provider_name = "deepseek"
        
    def generate(self, prompt: str):
        # Implement actual API call to DeepSeek here
        return f"Mock response from DeepSeek for: {prompt}"

from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    def process(self, input_data):
        pass

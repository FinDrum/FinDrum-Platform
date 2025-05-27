import pandas as pd
from findrum.interfaces import Operator

class CustomDataSource(Operator):
    
    def run(self, input_data):
        return self.__fetch()
    
    def __fetch(self, **kwargs):
        data = {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35]
        }
        return pd.DataFrame(data)
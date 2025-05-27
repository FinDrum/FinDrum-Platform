from findrum.interfaces import DataSource
import pandas as pd

class ExampleDataSource(DataSource):
    def fetch(self, **kwargs):
        return pd.DataFrame({"value": [1, 2, 3]})

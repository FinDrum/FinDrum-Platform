import pandas as pd
from findrum.interfaces import Operator

class SaveToCSVOperator(Operator):
    def run(self, input_data):
        if isinstance(input_data, pd.DataFrame):
            input_data.to_csv(self.params['path_output'], index=False)
        return input_data


class PrintCSVOperator(Operator):
    def run(self, input_data):
        df = pd.read_csv(self.params['path_input'])
        print("🖨️ CSV file content:")
        print(df)
        return df
from findrum.interfaces import Operator

class SumOperator(Operator):
    def run(self, input_data):
        return input_data["value"].sum()

class Show(Operator):
    def run(self, input_data):
        print(input_data)
        return input_data

from libs.base import ComputeUnit, ComputeInput, ComputeOutput
from pydantic import BaseModel
import time


class Sqr(ComputeUnit):
    class Input(ComputeInput):
        a: int

    class Output(ComputeOutput):
        result: int

    def compute(self, input_data: Input) -> Output:
        return self.Output(result=input_data.a * input_data.a)

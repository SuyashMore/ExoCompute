from libs.base import ComputeUnit, ComputeInput, ComputeOutput
from pydantic import BaseModel
import time


class Sqr(ComputeUnit):
    class Input(ComputeInput):
        a: int

    class Output(ComputeOutput):
        result: int

    def compute(self, input_data: Input) -> Output:
        start = time.time()
        x = 0.0
        compute_time = 1
        while time.time() - start < compute_time:
         # Useless math to keep the CPU busy
            x += (input_data.a * input_data.a) ** 0.5 / (input_data.a + 1)
        return self.Output(result=input_data.a * input_data.a)

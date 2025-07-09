from abc import ABC, abstractmethod
from pydantic import BaseModel

# Base input for all compute units
class ComputeInput(BaseModel):
    pass

# Base output for all compute units
class ComputeOutput(BaseModel):
    pass

# Abstract compute unit
class ComputeUnit(ABC):
    Input: type[ComputeInput]
    Output: type[ComputeOutput]

    @abstractmethod
    def compute(self, input_data: ComputeInput) -> ComputeOutput:
        pass

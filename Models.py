from dataclasses import dataclass

@dataclass
class MessageModel:
    MessageId: str
    Instruction: str
    Message: str

@dataclass
class TaskModel:
    Id: str
    TaskName: str
    ModelType: str
    ModelVariation: str
    Detection: str
    InputURL: str
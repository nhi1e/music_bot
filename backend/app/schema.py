from langchain_core.messages import AnyMessage
from typing import TypedDict, List

class ChatState(TypedDict):
    messages: List[AnyMessage]

from langchain_core.messages import AnyMessage
from typing import TypedDict, List

from typing_extensions import Annotated, TypedDict
from typing import Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

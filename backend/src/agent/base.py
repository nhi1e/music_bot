from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from typing import Any, List

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent


class BaseAgent:
    """Base class for all agents with shared LLM initialization"""

    @cached_property
    def _llm(self):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model="gpt-4o", temperature=0.7)

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the agent"""
        pass

    @property
    @abstractmethod
    def _prompt(self) -> str:
        """Return the prompt template for this agent"""
        pass

    @property
    @abstractmethod
    def _tools(self) -> List[Any]:
        """Return the tools for this agent"""
        pass

    @cached_property
    def _create_react_agent(self):
        return create_react_agent(
            model=self._llm,
            tools=self._tools,
            prompt=self._prompt,
            name=self.name,
        )

    def process(self, input_content: str) -> str:
        """
        Process input content using the agent's specialized capabilities.
        """
        messages = [HumanMessage(content=input_content)]
        result = self._create_react_agent.invoke({'messages': messages})
        return result['messages'][-1].content

    def _execute_tool_safely(self, tool_name: str, tool_args: dict, tool_call_id: str) -> ToolMessage:
        """Safely execute a tool and return a ToolMessage"""
        try:
            # Find matching tool
            tool = next(t for t in self._tools if t.name == tool_name)
            tool_output = tool.invoke(tool_args or {})
            
            if not tool_output or str(tool_output).strip() == "":
                tool_output = f"The {tool_name} tool completed but returned no results."
            
            print(f"[{self.name}] Tool output: {len(str(tool_output))} characters")
            
            return ToolMessage(
                tool_call_id=tool_call_id,
                content=str(tool_output)
            )
        except StopIteration:
            print(f"[{self.name}] Tool not found: {tool_name}")
            return ToolMessage(
                tool_call_id=tool_call_id,
                content=f"Error: Tool '{tool_name}' not found."
            )
        except Exception as e:
            print(f"[{self.name}] Tool error: {e}")
            return ToolMessage(
                tool_call_id=tool_call_id,
                content=f"Error executing {tool_name}: {str(e)}"
            )
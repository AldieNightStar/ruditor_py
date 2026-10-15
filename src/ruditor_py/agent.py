import typing

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain.agents import create_agent

class Agent:
    def __init__(self,
            url: str="http://localhost:1234/v1",
            api_key: str="...",
            model: str="lm-studio",
            sys_prompt: str = "You are helpful agent",
            temperature=0.6,
            reasoning="medium", # Can be: "low", "medium", "high"
        ):
        self.agent = None
        self.sys_prompt = sys_prompt
        self.tools: list[typing.Callable] = []
        self.history: list[typing.Any] = []
        self.llm = ChatOpenAI(
            base_url=url,
            api_key=api_key,  # type: ignore
            model=model,
            temperature=temperature,
            streaming=True,
            reasoning={
                "effort": reasoning,  # Default None; can be "low", "medium", or "high"
                "summary": "auto",  # Can be "auto", "concise", or "detailed"
            }
        )

    def _get_agent(self):
        if not self.agent:
            self._redefine_agent()
        return self.agent

    def _redefine_agent(self):
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.sys_prompt,
        )

    def _get_text_from_content(self, content):
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            if len(content) > 0:
                last_element = content[-1]
                if isinstance(last_element, str):
                    return last_element
                elif isinstance(last_element, dict):
                    return last_element.get('text', '')
                else:
                    return ""
            else:
                return ""
        else:
            return ""

    def set_tools(self, tools: list):
        self.tools = tools
        self._redefine_agent()

    def reset(self):
        self.history = []

    async def query(self, user_query: str) -> str:
        self.history.append(HumanMessage(content=user_query))

        inputs = {"messages": self.history}
        agent = self._get_agent()

        latest_message: AIMessage = None  # type: ignore

        async for event in agent.astream(inputs, stream_mode="updates"):  # type: ignore
            for node_name, node_output in event.items():
                if isinstance(node_output, dict) and "messages" in node_output:
                    for msg in node_output["messages"]:
                        # Append agent/tool steps to our maintained history list
                        self.history.append(msg)
                        if isinstance(msg, AIMessage):
                            latest_message = msg
        content = latest_message.content if latest_message else ""
        return self._get_text_from_content(content)


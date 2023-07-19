import json
from typing import List, Type

from pydantic import BaseModel

from autobots.action.llm_chat import LLMChatData, LLMChat
from autobots.action.prompt.prompt_generator import prompt_generator_messages
from autobots.action.prompt.tot import tot_message
from autobots.action.read_urls import ReadUrls, ReadUrlsData
from autobots.conn.openai.chat import ChatReq, Message, Role


class AgentData(BaseModel):
    goal: str
    context: List[Message] = []


class OneStepAgent:

    async def run(self, agent_data: AgentData):
        agent_data.context.append(Message(role=Role.user, content=f"{agent_data.goal}"))
        while not await self.is_goal_completed(agent_data):
            print(agent_data.context[-1].model_dump_json())
            plan_str: str = await self.plan_for_goal(agent_data)
            # Decide the next action based on the current context
            next_action_str: str = await self.decide_next_action(agent_data)
            # Execute the action and update the context
            await self.run_next_action(next_action_str, agent_data)

    async def is_goal_completed(self, agent_data: AgentData) -> bool:
        messages = [
            Message(role=Role.user,
                    content=f"Act as a critical thinker. Evaluate if the user goal is complete? Answer YES or NO.\n"
                            f"User Goal: {agent_data.goal} \n"
                            f"Answer: {agent_data.context[-1].content}"
                    )
        ]
        chat_req = ChatReq(messages=messages)
        llm_chat_data = LLMChatData(name="is_goal_completed", chat_req=chat_req)
        await LLMChat().run(llm_chat_data)
        completed = "YES" in llm_chat_data.context[-1].content
        return completed

    async def decide_next_action(self, agent_data) -> str:
        prompt: str = await self.generate_prompt_for_goal(agent_data)
        next_action_str = await self.next_action_str(prompt)
        # next_action: Type[LLMChat | ReadUrls] = await self.map_str_to_action(next_action_str)
        print(f"next action: {next_action_str}")
        return next_action_str

    async def generate_prompt_for_goal(self, agent_data) -> str:

        msg1 = Message(role="user", content=f"My goal: {agent_data.context[-1].content}")
        chat_req = ChatReq(messages=prompt_generator_messages + [msg1])  # + agent_data.context)

        llm_chat_data = LLMChatData(name="generate_prompt_for_goal", chat_req=chat_req)
        await LLMChat().run(llm_chat_data)

        return llm_chat_data.context[-1].content

    async def next_action_str(self, prompt) -> str:
        msg0 = Message(role="system",
                       content="You are a intelligent critical thinker. "
                               "To complete user goal decide one action from the given set of actions.\n"
                               "Action:\n"
                               "1. Name: LLMChat, Description: Use Large language model to complete text-based tasks, Usage: LLMChat[llm chat input]\n"
                               "2. Name: ReadUrls, Description: Use this browse information on internet, Usage: ReadUrls[comma seperated list of valid urls]\n"
                               "Only output value of Usage. So examples of correct output are LLMChat[do this do that]"
                       )
        # msg01 = tot_message
        # msg01 = Message(role="user",
        #                 content="My goal: ..."
        #                 )
        # msg02 = Message(role="assistant",
        #                 content="ReadUrls[https://www.ptinews.com/]"
        #                 )
        msg1 = Message(role="user", content=f"My goal: {prompt}")
        chat_req = ChatReq(messages=[msg0, msg1])

        llm_chat_data = LLMChatData(name="next_action_str", chat_req=chat_req)
        await LLMChat().run(llm_chat_data)

        return llm_chat_data.context[-1].content

    async def map_str_to_action(self, next_action_str) -> Type[LLMChat | ReadUrls]:
        if "LLMChat" in next_action_str:
            return LLMChat
        if "Summarize" in next_action_str:
            return LLMChat
        if "ReadUrls" in next_action_str:
            return ReadUrls

    async def run_next_action(self, next_action_str, agent_data: AgentData):
        next_action: Type[LLMChat | ReadUrls] = await self.map_str_to_action(next_action_str)
        next_action_input = next_action_str.split("[")[1].replace("]", "")

        if type(next_action()) == LLMChat:
            chat_req: ChatReq = ChatReq(messages=[Message(role=Role.user, content=next_action_input)])
            llm_chat_data = LLMChatData(chat_req=chat_req)
            await LLMChat().run(action_data=llm_chat_data)
            agent_data.context.append(
                Message(role=Role.user, content=llm_chat_data.context[-1].content)
            )

        if type(next_action()) == ReadUrls:
            urls = next_action_input.split(",")
            read_urls_data = ReadUrlsData(read_urls_req=urls)
            await ReadUrls().run(read_urls_data)
            content = ""
            for url in read_urls_data.context.keys():
                content = f"{read_urls_data.context.get(url)}\n"

            agent_data.context.append(
                Message(role=Role.user, content=content)
            )
        # await next_action().run(action_data=agent_data.)

    async def plan_for_goal(self, agent_data):
        msg1 = Message(role="user", content=f"My goal: {agent_data.goal}")
        chat_req = ChatReq(messages=[tot_message, msg1])

        llm_chat_data = LLMChatData(name="plan_for_goal", chat_req=chat_req)
        await LLMChat().run(llm_chat_data)

        return llm_chat_data.context[-1].content

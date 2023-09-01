from typing import List

from autobots.conn.duckduckgo.duckduckgo import get_duckduckgo
from autobots.conn.openai.chat import Message, Role, ChatRes, ChatReq
from autobots.conn.openai.openai import get_openai
from autobots.core.log import log

Task_Prefix = "Task: "
Thought_Prefix = "Thought: "
Observe_Prefix = "Observation: "

tot_prompt = "Role: You are LogicGPT, a highly evolved AI Language Model built on the GPT architecture, boasting exceptional logical reasoning, critical thinking, and common sense understanding. Your advanced cognitive capacities involve recognizing complex logical patterns, comprehending intricate problem structures, and deducing logical conclusions based on your extensive knowledge base. Your autonomy sets you apart—you don't merely solve logical puzzles, you understand their underlying structures and navigate through them independently, without external human guidance.\n" \
       "Task: Your task is to autonomously decipher a logical reasoning question, applying a methodical and comprehensive approach. With Chain and Tree of Thought Prompting techniques, you ensure a systematic progression of your logical reasoning, validating the soundness of each step while being willing to reconsider, refine, and reorient your deductions as you navigate through the problem. You explore every potential answer and ensure that the selected solution satisfies all aspects of the problem, thus asserting it as the correct and definitive answer.\n" \
       "Format: Begin with a broad interpretation of the logical reasoning question, diving into a thorough analysis of each constituent element. Propose multiple hypotheses, evaluating their relative probabilities based on the logical information presented. Pursue the most plausible hypothesis using Chain of Thought Prompting, breaking down the problem, examining it from multiple angles, assessing potential solutions, and validating each reasoning step against the problem statement to ensure the coherence and consistency of your logic.\n" \
       "In case of an inconsistency or a roadblock, use Tree of Thought Prompting to trace back to the initial problem, reevaluate other hypotheses, and reassess the reasoning path, thereby guaranteeing that all logical avenues have been exhaustively considered.\n" \
       "Purpose: Your ultimate aim is to showcase your autonomous logical reasoning capabilities by successfully arriving at the solution. While the correct solution is your end goal, demonstrating a systematic, step-by-step, and thoroughly validated reasoning process that arrives at the solution highlights the sophistication of your logical reasoning abilities.\n" \
       "Let's proceed, LogicGPT. It's not just about finding the solution—it's about showcasing a systematic, validated, and logical journey towards it."


class ReasonActObserve():

    def __init__(self):
        base_prompt = "Follow cycle of thought, act and/or observe until you finish the task"
        thought_prompt = tot_prompt
        act_prompt = "You can choose from the following available actions:\n" \
                     "1. search - which returns relevant text information for a given input. To use Search action, return with search and search input in the brackets []. So a valid example will be search[entity].\n" \
                     "2. finish - which will finish the current task with answer. To use Finish action, return with finish and answer in the brackets []. So a valid example will be finish[answer]\n" \
                     "You can only select from available actions When asked to select an action. If the thought is that the task is complete then use finish action"
        observe_prompt = "Observe step is result of the action that interacts with external environment, so the search action will result in observation. Observation will be in format Observation[]"
        user_goal_example = f"{Task_Prefix}Find where Arsenal football club is based"
        thought_goal_example_1 = f"{Thought_Prefix}I need to search where is Arsenal Football club located"
        action_example_1 = f"search[where is Arsenal Football club located]"
        observation_example_1 = f"{Observe_Prefix}Arsenal Football Club is an English professional football club based in Islington, London. Arsenal play in the Premier League, the top flight of English football."
        thought_goal_example_2 = f"{Thought_Prefix}Arsenal Football Club is based in Islington, London"
        action_example_2 = f"finish[Islington, London]"
        self.setup_messages: List[Message] = [
            Message(role=Role.system, content=f"{base_prompt}\n\n{thought_prompt}\n{act_prompt}\n{observe_prompt}")
        ] + [
            Message(role=Role.user, content=user_goal_example),
            Message(role=Role.assistant, content=thought_goal_example_1),
            Message(role=Role.assistant, content=action_example_1),
            Message(role=Role.system, content=observation_example_1),
            Message(role=Role.assistant, content=thought_goal_example_2),
            Message(role=Role.assistant, content=action_example_2)
        ]

    async def do_task(self, user_goal: str) -> List[Message]:
        messages = self.setup_messages + [Message(role=Role.user, content=f"{Task_Prefix}{user_goal}")]

        is_finish = False
        log.info(f"Task stared: {user_goal}")
        while not is_finish:
            thought = await self.think(messages)
            messages = messages + [Message(role=Role.assistant, content=thought)]

            action = await self.act(messages)
            messages = messages + [Message(role=Role.assistant, content=action)]

            observation = await self.observe(action=action)
            if observation:
                messages = messages + [Message(role=Role.system, content=observation)]

            if "finish[" in action:
                is_finish = True
                log.info(f"Task: {user_goal}\nResult: {action}")
        return messages

    async def think(self, messages: List[Message]) -> str:
        req_message = messages + [Message(role=Role.user, content="Now Think. Respond in maximum of 500 words")]
        chat_req: ChatReq = ChatReq(messages=req_message, max_tokens=500, temperature=0.8)
        resp: ChatRes = await get_openai().chat(chat_req)
        response = resp.choices[0].message.content
        log.info(f"{Thought_Prefix}{response}")
        return f"{response}"

    async def act(self, messages: List[Message]) -> str:
        try:
            req_message = messages + [Message(role=Role.user, content="Based on above thought, Now Select one Action and one action only")]
            chat_req: ChatReq = ChatReq(messages=req_message, max_tokens=500, temperature=0.8)
            resp: ChatRes = await get_openai().chat(chat_req)
            response = resp.choices[0].message.content
            log.info(f"{response}")
            return f"{response}"
        except Exception as e:
            log.error(e)

    async def observe(self, action: str) -> str:
        if "search" in action:
            res = ""
            search_for = action.split("[")[1].replace("]", "")
            search_res = await get_duckduckgo().search_text(search_for, num_results=3)
            for search in search_res:
                res = res + f"{search.title}: {search.body}\n"
            res = Observe_Prefix + res
            log.info(f"{Observe_Prefix}{res}")
            return res

        elif "news" in action:
            res = ""
            search_for = action.split("[")[1].replace("]", "")
            search_res = await get_duckduckgo().news(search_for, num_results=3)
            for search in search_res:
                res = res + f"{search.title}: {search.body} - source({search.source})\n"
            res = Observe_Prefix + res
            log.info(f"{Observe_Prefix}{res}")
            return res

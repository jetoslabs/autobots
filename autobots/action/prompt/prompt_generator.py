from typing import List

from autobots.conn.openai.chat import Message, Role

prompt_generator_messages: List[Message] = [
    Message(role=Role.system, content="Act as an expert Prompt generator for Large Language Model. Think step by step and generate a prompt for user given task."),
    Message(role=Role.user, content="Generate a prompt to prime Large Language Model for a task. Output should only contain the prompt.")
]
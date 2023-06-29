from typing import List

from autobots.conn.openai.chat import Message, Role

blog_writer_messages: List[Message] = [
    Message(role=Role.system, content="Act as an expert Blog writer. Think step by step and write a blog for topic given by user."),
    Message(role=Role.user, content="Act as an expert blog writer and write blog for topic.")
]
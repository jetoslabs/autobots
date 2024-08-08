import queue
import threading
import asyncio  # Changed from asyncio to asyncio
import requests
from pydantic import BaseModel
from src.autobots.action.action_type.action_factory import ActionFactory

class PollDoc(BaseModel):
    id: str
    name: str
    description: str

class PollCreate(BaseModel):
    name: str
    description: str

class PollUpdate(BaseModel):
    name: str
    description: str

class PollFind(BaseModel):
    id: str

# Define the OutputQueue
class OutputQueue:
    def __init__(self):
        self.queue = queue.Queue()
    
    def add_message(self, message):
        self.queue.put(message)
    
    def get_message(self):
        return self.queue.get()
    
    def is_empty(self):
        return self.queue.empty()

    def pop(self):
        self.queue.pop()

# Define the WorkflowAgent

# Define the PollingAgent
class PollingAgent:
    def __init__(self, input_action, output_queue, polling_interval=5):
        self.input_action = input_action
        self.output_queue = output_queue
        self.polling_interval = polling_interval
        self._stop_event = threading.Event()
    
    def start(self):
        self.thread = threading.Thread(target=self._poll)
        self.thread.start()
    
    async def _poll(self):
        while not self._stop_event.is_set():
            # run llm action here
            action_result = await ActionFactory.run_in_background(self.input_action)
            self.output_queue.add_message(action_result)
            asyncio.sleep(self.polling_interval)
    
    def stop(self):
        self._stop_event.set()
        self.thread.join()

# Example usage

class PollGraph:
    def __init__(self, input_action, workflow_agent, pollgraph_result=[]):
        self.pollgraph_result = pollgraph_result
        self.input_action = input_action
        self.workflow_agent = workflow_agent
        self.output_queue = OutputQueue()
        self.polling_agent = PollingAgent(self.output_queue, polling_interval=5)

    
    # Define the API URL
    async def run_in_background(self):
        self.polling_agent.start()

        # Simulate a separate thread or process for the WorkflowAgent
        async def process_queue():
            while True:
                if not self.output_queue.is_empty():
                    message = self.output_queue.get_message()
                    workflow_result = await self.workflow_agent.run_in_background(message)
                    self.output_queue.pop()
                    self.pollgraph_result.append(workflow_result)
                else:
                    asyncio.sleep(1)

        self.processing_thread = threading.Thread(target=process_queue)
        self.processing_thread.start()


    def stop(self):
        # Stop the polling agent
        self.polling_agent.stop()
        # Stop the processing thread
        self.processing_thread.join()

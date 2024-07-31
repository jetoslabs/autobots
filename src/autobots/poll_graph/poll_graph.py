import queue
import threading
import time
import requests
from pydantic import BaseModel

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

# Define the WorkflowAgent
class WorkflowAgent:
    def process_message(self, message):
        print(f"Processing message: {message}")
        # Implement message processing logic here
        time.sleep(2)  # Simulate some processing time
        print(f"Finished processing message: {message}")

# Define the PollingAgent
class PollingAgent:
    def __init__(self, api_url, output_queue, polling_interval=5):
        self.api_url = api_url
        self.output_queue = output_queue
        self.polling_interval = polling_interval
        self._stop_event = threading.Event()
    
    def start(self):
        self.thread = threading.Thread(target=self._poll)
        self.thread.start()
    
    def _poll(self):
        while not self._stop_event.is_set():
            # run llm action here
            # try:
            #     # Poll the API
            #     response = requests.get(self.api_url)
            #     if response.status_code == 200:
            #         data = response.json()
            #         # Assuming the API returns a list of messages
            #         for message in data:
            #             self.output_queue.add_message(message)
            # except Exception as e:
            #     print(f"Error polling API: {e}")
            time.sleep(self.polling_interval)
    
    def stop(self):
        self._stop_event.set()
        self.thread.join()

# Example usage
if __name__ == "__main__":
    output_queue = OutputQueue()
    workflow_agent = WorkflowAgent()
    
    # Define the API URL
    api_url = "http://example.com/api/messages"
    
    polling_agent = PollingAgent(api_url, output_queue, polling_interval=5)
    polling_agent.start()

    # Simulate a separate thread or process for the WorkflowAgent
    def process_queue():
        while True:
            if not output_queue.is_empty():
                message = output_queue.get_message()
                workflow_agent.process_message(message)
            else:
                time.sleep(1)

    processing_thread = threading.Thread(target=process_queue)
    processing_thread.start()

    # Allow the system to run for a while
    time.sleep(60)

    # Stop the polling agent
    polling_agent.stop()
    # Stop the processing thread
    processing_thread.join()

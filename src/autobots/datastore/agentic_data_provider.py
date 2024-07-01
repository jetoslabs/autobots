from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import json
from typing import Callable, AsyncGenerator, List

# Mocking get_tiktoken function for the example
class Tokenizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def token_count(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

def get_tiktoken():
    tokenizer = AutoTokenizer.from_pretrained("chentong00/propositionizer-wiki-flan-t5-large")
    return Tokenizer(tokenizer)

class DataProvider:

    def __init__(self):
        pass

    @staticmethod
    async def read_data_line_by_line(data: str, delimiter: str = "\n") -> AsyncGenerator[str, None]:
        if not delimiter:
            yield data
        else:
            lines = [line + delimiter for line in data.split(delimiter)]
            lines[-1] = lines[-1].rstrip(delimiter)

            for line in lines:
                if line == delimiter:
                    continue
                yield line

    @staticmethod
    async def create_data_chunks(
            data: str,
            chunk_func: Callable[[str], AsyncGenerator[str, None]],
            chunk_token_size: int = 512
    ) -> AsyncGenerator[str, None]:
        chunk = ""
        count = 0
        # iter over chunks
        async for part in chunk_func(data):
            if count >= chunk_token_size:
                yield chunk
                chunk = ""
                count = 0

            # count tokens
            token_count = get_tiktoken().token_count(part)
            count += token_count

            chunk += part

        # yield last chunk
        yield chunk

# Initialize model and tokenizer
model_name = "chentong00/propositionizer-wiki-flan-t5-large"

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

# Input text
input_text = (
    "I love dogs. They are amazing. Cats must be the easiest pets around. "
    "Tesla robots are advanced now with AI. They will take us to Mars."
)

# Chunking the input text
async def process_chunks(input_text: str):
    data_provider = DataProvider()
    async for chunk in data_provider.create_data_chunks(input_text, data_provider.read_data_line_by_line):
        input_ids = tokenizer(chunk, return_tensors="pt").input_ids
        outputs = model.generate(input_ids.to(device), max_new_tokens=512).cpu()
        output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        try:
            prop_list = json.loads(output_text)
            print(json.dumps(prop_list, indent=2))
        except json.JSONDecodeError:
            print("[ERROR] Failed to parse output text as JSON.")
            print(output_text)


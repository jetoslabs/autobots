from typing import List
from sentence_transformers import SentenceTransformer, util
import spacy
from src.autobots.conn.tiktoken.tiktoken import get_tiktoken
from typing import Callable, AsyncGenerator
from src.autobots.datastore.data_provider import DataProvider
class SentenceTransformersSimilarity:
    
    def __init__(self, model="all-MiniLM-L6-v2", similarity_threshold=0.2):
        self.model = SentenceTransformer(model)
        self.similarity_threshold = similarity_threshold
    
    def similarities(self, sentences: List[str]):
        # Encode all sentences
        embeddings = self.model.encode(sentences)
        
        # Calculate cosine similarities for neighboring sentences
        similarities = []
        
        for i in range(1, len(embeddings)):
            sim = util.pytorch_cos_sim(embeddings[i - 1], embeddings[i]).item()
            similarities.append(sim)
        
        return similarities

class SpacySentenceSplitter:
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def split(self, text: str) -> List[str]:
        doc = self.nlp(text)
        return [str(sent).strip() for sent in doc.sents]

class SimilarSentenceSplitter:
    
    def __init__(self, similarity_model, sentence_splitter):
        self.model = similarity_model
        self.sentence_splitter = sentence_splitter
    
    def split_text(self, text: str, group_max_sentences=5) -> List[str]:
        """
        group_max_sentences: The maximum number of sentences in a group.
        """
        sentences = self.sentence_splitter.split(text)
        
        if len(sentences) == 0:
            return []

        similarities = self.model.similarities(sentences)
        
        # The first sentence is always in the first group.
        groups = [[sentences[0]]]
        
        # Using the group min/max sentences constraints,
        # group together the rest of the sentences.
        for i in range(1, len(sentences)):
            if len(groups[-1]) >= group_max_sentences:
                groups.append([sentences[i]])
            elif similarities[i - 1] >= self.model.similarity_threshold:
                groups[-1].append(sentences[i])
            else:
                groups.append([sentences[i]])
        
        return [" ".join(g) for g in groups]

class SemanticDataProvider(DataProvider):
    
    def __init__(self, model_name="all-MiniLM-L6-v2", similarity_threshold=0.2):
        self.similarity_model = SentenceTransformersSimilarity(model=model_name, similarity_threshold=similarity_threshold)
        self.sentence_splitter = SpacySentenceSplitter()
        self.similar_sentence_splitter = SimilarSentenceSplitter(self.similarity_model, self.sentence_splitter)
    
    async def create_semantic_chunks(self, text: str, chunk_token_size: int = 512) -> AsyncGenerator[str, None]:
        chunks = self.similar_sentence_splitter.split_text(text)
        chunk = ""
        count = 0
        for part in chunks:
            token_count = get_tiktoken().token_count(part)
            if count + token_count > chunk_token_size:
                yield chunk
                chunk = ""
                count = 0
            count += token_count
            chunk += part + " "
        if chunk:
            yield chunk
            
            
    #         def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
    #     super().__init__()
    #     self.model = SentenceTransformer(model_name)
    #     self.nlp = spacy.load('en_core_web_sm')

    # async def create_semantic_chunks(self, text: str, chunk_token_size: int = 512) -> AsyncGenerator[str, None]:
    #     sentences = [sent.text for sent in self.nlp(text).sents]
    #     embeddings = self.model.encode(sentences, convert_to_tensor=True)
        
    #     chunk = ""
    #     count = 0
    #     for i, sentence in enumerate(sentences):
    #         token_count = get_tiktoken().token_count(sentence)
    #         if count + token_count > chunk_token_size:
    #             yield chunk
    #             chunk = ""
    #             count = 0
    #         count += token_count
    #         chunk += sentence + " "
    #     if chunk:
    #         yield chunk
from enum import Enum 
from typing import List, Optional, Dict, Sequence, Tuple
from pydantic import Field, root_validator
from src.autobots.conn.chroma.chroma import Document, Chroma
from typing import Generic, TypeVar, Dict, Optional, List,  Dict, Any


class ByteStore:
    """A simple in-memory ByteStore implementation."""

    def __init__(self):
        self.store: Dict[str, bytes] = {}

    def put(self, key: str, value: bytes) -> None:
        """Store the byte value under the given key."""
        self.store[key] = value

    def get(self, key: str) -> Optional[bytes]:
        """Retrieve the byte value for the given key, or None if the key doesn't exist."""
        return self.store.get(key)

    def delete(self, key: str) -> None:
        """Delete the byte value for the given key."""
        if key in self.store:
            del self.store[key]


TKey = TypeVar('TKey')
TValue = TypeVar('TValue')


class BaseStore(Generic[TKey, TValue]):
    """A simple in-memory BaseStore implementation."""

    def __init__(self):
        self.store: Dict[TKey, TValue] = {}

    def put(self, key: TKey, value: TValue) -> None:
        """Store the value under the given key."""
        self.store[key] = value

    def get(self, key: TKey) -> Optional[TValue]:
        """Retrieve the value for the given key, or None if the key doesn't exist."""
        return self.store.get(key)

    def delete(self, key: TKey) -> None:
        """Delete the value for the given key."""
        if key in self.store:
            del self.store[key]

    def mget(self, keys: List[TKey]) -> List[Optional[TValue]]:
        """Retrieve multiple values for the given keys."""
        return [self.store.get(key) for key in keys]

    async def aget(self, key: TKey) -> Optional[TValue]:
        """Asynchronously retrieve the value for the given key."""
        return self.get(key)

    async def amget(self, keys: List[TKey]) -> List[Optional[TValue]]:
        """Asynchronously retrieve multiple values for the given keys."""
        return self.mget(keys)
    
    def mset(self, key_value_pairs: Sequence[Tuple[str, TValue]]) -> None:
        """Set the values for the given keys.

        Args:
            key_value_pairs (Sequence[Tuple[str, V]]): A sequence of key-value pairs.

        Returns:
            None
        """
        for key, value in key_value_pairs:
            self.store[key] = value

def create_kv_docstore(byte_store: ByteStore) -> BaseStore[str, Document]:
    """Create a Key-Value Document Store using a ByteStore as the backend."""

    class KVDocStore(BaseStore[str, Document]):
        def put(self, key: str, value: Document) -> None:
            byte_value = value.content.encode('utf-8')
            byte_store.put(key, byte_value)

        def get(self, key: str) -> Optional[Document]:
            byte_value = byte_store.get(key)
            if byte_value is not None:
                return Document(byte_value.decode('utf-8'))
            return None

        def delete(self, key: str) -> None:
            byte_store.delete(key)

        def mget(self, keys: List[str]) -> List[Optional[Document]]:
            return [self.get(key) for key in keys]

        async def aget(self, key: str) -> Optional[Document]:
            return self.get(key)

        async def amget(self, keys: List[str]) -> List[Optional[Document]]:
            return self.mget(keys)

    return KVDocStore()



class SearchType(str, Enum):
    """Enumerator of the types of search to perform."""

    similarity = "similarity"
    """Similarity search."""
    mmr = "mmr"
    """Maximal Marginal Relevance reranking of similarity search."""

class MultiVectorRetriever():
    """Retrieve from a set of multiple embeddings for the same document."""

    vectorstore: Chroma
    """The underlying vectorstore to use to store small chunks
    and their embedding vectors"""
    byte_store: Optional[ByteStore] = None
    """The lower-level backing storage layer for the parent documents"""
    docstore: BaseStore[str, Document]
    """The storage interface for the parent documents"""
    id_key: str = "doc_id"
    search_kwargs: dict = Field(default_factory=dict)
    """Keyword arguments to pass to the search function."""
    search_type: SearchType = SearchType.similarity
    """Type of search to perform (similarity / mmr)"""
    def __init__(self,vectorstore,docstore,id_key):
        self.vectorstore = vectorstore
        self.docstore=docstore
        self.id_key=id_key
    @root_validator(pre=True)
    def shim_docstore(cls, values: Dict) -> Dict:
        byte_store = values.get("byte_store")
        docstore = values.get("docstore")
        if byte_store is not None:
            docstore = create_kv_docstore(byte_store)
        elif docstore is None:
            raise Exception("You must pass a `byte_store` parameter.")
        values["docstore"] = docstore
        return values

    async def _get_relevant_documents(
        self, query: str) -> List[Document]:
        """Get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        if self.search_type == SearchType.mmr:
            sub_docs = self.vectorstore.max_marginal_relevance_search(
                query
            )
        else:
            sub_docs = await self.vectorstore.similarity_search(query)

        # We do this to maintain the order of the ids that are returned
        ids = []
        for d in sub_docs:
            if self.id_key in d.metadata and d.metadata[self.id_key] not in ids:
                ids.append(d.metadata[self.id_key])
        result =[]
        for id in ids:
            data = await self.s3.get(f"{self._get_s3_basepath()}/{id}")
            result.append(data)
        # docs = self.docstore.mget(ids)
        # return [d for d in docs if d is not None]
        return result

    async def _aget_relevant_documents(
        self, query: str) -> List[Document]:
        """Asynchronously get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        if self.search_type == SearchType.mmr:
            sub_docs = await self.vectorstore.amax_marginal_relevance_search(
                query, **self.search_kwargs
            )
        else:
            sub_docs = await self.vectorstore.asimilarity_search(
                query, **self.search_kwargs
            )

        # We do this to maintain the order of the ids that are returned
        ids = []
        for d in sub_docs:
            if self.id_key in d.metadata and d.metadata[self.id_key] not in ids:
                ids.append(d.metadata[self.id_key])
        docs = await self.docstore.amget(ids)
        return [d for d in docs if d is not None]
    

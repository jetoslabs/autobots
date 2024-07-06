# from unstructured.partition.pdf import partition_pdf
import base64
import uuid
import os
from tests.datastore.chroma import Chroma, Document
from tests.datastore.multi_vector import MultiVectorRetriever, BaseStore
from src.autobots.conn.openai.openai_embeddings.openai_embeddings import OpenaiEmbeddings
from src.autobots.datastore.data_provider import DataProvider
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import asyncio

from src.autobots.conn.openai.openai_client import get_openai

from src.autobots.conn.aws.s3 import get_s3
from src.autobots.conn.pinecone.pinecone import get_pinecone
from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io
from src.autobots.core.settings import Settings, SettingsProvider

client = OpenAI(api_key=SettingsProvider.sget().OPENAI_API_KEY)

def summarize_element(element):
    prompt_text = f"""You are an assistant tasked with summarizing tables and text for retrieval. \
These summaries will be embedded and used to retrieve the raw text or table elements. \
Give a concise summary of the table or text that is well optimized for retrieval. Table or text: {element}"""

    # Call the OpenAI API to generate the summary
    response = client.chat.completions.create(model="gpt-4-turbo",
                                               messages=[
            {"role": "system", "content": "You are an assistant tasked with summarizing tables and text for retrieval."},
            {"role": "user", "content": prompt_text}
        ],
    temperature=0,
    max_tokens=150) # Adjust the token limit based on your needs)

    # Extract and return the summary from the response
    summary = response.choices[0].message.content.strip()
    return summary

def summarize_text(texts, max_concurrency=5):
    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = [executor.submit(summarize_element, text) for text in texts]
        summaries = [future.result() for future in futures]
    return summaries


# def extract_pdf_elements(path, fname):
#     """
#     Extract images, tables, and chunk text from a PDF file.
#     path: File path, which is used to dump images (.jpg)
#     fname: File name
#     """
#     return partition_pdf(
#         filename=path + fname,
#         extract_images_in_pdf=False,
#         infer_table_structure=True,
#         chunking_strategy="by_title",
#         max_characters=4000,
#         new_after_n_chars=3800,
#         combine_text_under_n_chars=2000,
#         image_output_dir_path=path,
#     )


# Categorize elements by type
def categorize_elements(raw_pdf_elements):
    """
    Categorize extracted elements from a PDF into tables and texts.
    raw_pdf_elements: List of unstructured.documents.elements
    """
    tables = []
    texts = []
    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            tables.append(str(element))
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            texts.append(str(element))
    return texts, tables


# File path
fpath = "/Users/khushalsethi/godelsales/autobots/tests/resources/datastore/cj"
fname = "cj.pdf"


s3 = get_s3()
pinecone = get_pinecone()
unstructured = get_unstructured_io()
# Get elements
# raw_pdf_elements = extract_pdf_elements(fpath, fname)

# # Get text, tables
# texts, tables = categorize_elements(raw_pdf_elements)


# class PyPDFParser(BaseBlobParser):
#     """Load `PDF` using `pypdf`"""

#     def __init__(
#         self, password: Optional[Union[str, bytes]] = None, extract_images: bool = False
#     ):
#         self.password = password
#         self.extract_images = extract_images

#     def lazy_parse(self, blob: Blob) -> Iterator[Document]:  # type: ignore[valid-type]
#         """Lazily parse the blob."""
#         try:
#             import pypdf
#         except ImportError:
#             raise ImportError(
#                 "`pypdf` package not found, please install it with "
#                 "`pip install pypdf`"
#             )

#         with blob.as_bytes_io() as pdf_file_obj:  # type: ignore[attr-defined]
#             pdf_reader = pypdf.PdfReader(pdf_file_obj, password=self.password)
#             yield from [
#                 Document(
#                     page_content=page.extract_text()
#                     + self._extract_images_from_page(page),
#                     metadata={"source": blob.source, "page": page_number},  # type: ignore[attr-defined]
#                 )
#                 for page_number, page in enumerate(pdf_reader.pages)
#             ]


# class PyPDFLoader(BasePDFLoader):
#     """Load PDF using pypdf into list of documents.

#     Loader chunks by page and stores page numbers in metadata.
#     """

# [docs]    def __init__(
#         self,
#         file_path: str,
#         password: Optional[Union[str, bytes]] = None,
#         headers: Optional[Dict] = None,
#         extract_images: bool = False,
#     ) -> None:
#         """Initialize with a file path."""
#         try:
#             import pypdf  # noqa:F401
#         except ImportError:
#             raise ImportError(
#                 "pypdf package not found, please install it with " "`pip install pypdf`"
#             )
#         super().__init__(file_path, headers=headers)
#         self.parser = PyPDFParser(password=password, extract_images=extract_images)


# [docs]    def lazy_load(
#         self,
#     ) -> Iterator[Document]:
#         """Lazy load given path as pages."""
#         if self.web_path:
#             blob = Blob.from_data(open(self.file_path, "rb").read(), path=self.web_path)  # type: ignore[attr-defined]
#         else:
#             blob = Blob.from_path(self.file_path)  # type: ignore[attr-defined]
#         yield from self.parser.parse(blob)

# loader = PyPDFLoader(fpath + fname)
# docs = loader.load()
# tables = [] # Ignore w/ basic pdf loader
# texts = [d.page_content for d in docs]
texts=["In an era dominated by screens and digital content, the simple act of reading a book may seem quaint or even obsolete. Yet, the intrinsic value of books has endured throughout centuries, transcending the rapid changes in technology and lifestyle. Reading books is not just a leisure activity; it is a multifaceted endeavor that offers profound benefits for our cognitive abilities, emotional health, and social skills. This essay delves into the myriad advantages of reading, underscoring its importance in our increasingly digital world."]
# # Optional: Enforce a specific token size for texts
# text_splitter = DataProvider.read_text_splitter(
#     chunk_size=4000, chunk_overlap=0
# )
# joined_texts = " ".join(texts)
# texts_4k_token = text_splitter.split_text(joined_texts)
texts_4k_token =texts




def encode_image(image_path):
    """Getting the base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def image_summarize(img_base64, prompt):
    """Make image summary"""

    response = client.chat.completions.create(model="gpt-4-vision-preview",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "", "image": img_base64}
    ])

    return response.choices[0].message.content.strip()


def generate_img_summaries(path):
    """
    Generate summaries and base64 encoded strings for images
    path: Path to list of .jpg files extracted by Unstructured
    """

    # Store base64 encoded images
    img_base64_list = []

    # Store image summaries
    image_summaries = []

    # Prompt
    prompt = """You are an assistant tasked with summarizing images for retrieval. \
    These summaries will be embedded and used to retrieve the raw image. \
    Give a concise summary of the image that is well optimized for retrieval."""

    # Apply to images
    for img_file in sorted(os.listdir(path)):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(path, img_file)
            base64_image = encode_image(img_path)
            img_base64_list.append(base64_image)
            image_summaries.append(image_summarize(base64_image, prompt))

    return img_base64_list, image_summaries


# Image summaries
img_base64_list, image_summaries = generate_img_summaries(fpath)


def generate_text_summaries(texts, tables, summarize_texts=False):
    """
    Summarize text elements
    texts: List of str
    tables: List of str
    summarize_texts: Bool to summarize texts
    """

    # # Prompt
    # prompt_text = """You are an assistant tasked with summarizing tables and text for retrieval. \
    # These summaries will be embedded and used to retrieve the raw text or table elements. \
    # Give a concise summary of the table or text that is well optimized for retrieval. Table or text: {element} """

    # Text summary chain

    # Initialize empty summaries
    text_summaries = []
    table_summaries = []

    # Apply to text if texts are provided and summarization is requested
    if texts and summarize_texts:
        text_summaries = summarize_text(texts)
    elif texts:
        text_summaries = texts

    # Apply to tables if tables are provided
    if tables:
        table_summaries = summarize_texts(tables)

    return text_summaries, table_summaries
text_summaries, table_summaries = generate_text_summaries(
    texts_4k_token,None, summarize_texts=True
)



async def create_multi_vector_retriever(
    vectorstore, text_summaries, texts, table_summaries, tables, image_summaries, images
):
    """
    Create retriever that indexes summaries, but returns raw images or texts
    """
    store= BaseStore()
    # Initialize the storage layer
    id_key = "doc_id"

    # Create the multi-vector retriever
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )

    # Helper function to add documents to the vectorstore and docstore
    async def add_documents(retriever, doc_summaries, doc_contents):
        doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
        summary_docs = [
            Document(page_content=s, metadata={id_key: doc_ids[i]})
            for i, s in enumerate(doc_summaries)
        ]
        await retriever.vectorstore.add_documents(summary_docs)
        retriever.docstore.mset(list(zip(doc_ids, doc_contents)))

    # Add texts, tables, and images
    # Check that text_summaries is not empty before adding
    if text_summaries:
       await add_documents(retriever, text_summaries, texts)
    # Check that table_summaries is not empty before adding
    if table_summaries:
       await add_documents(retriever, table_summaries, tables)
    # Check that image_summaries is not empty before adding
    if image_summaries:
       await add_documents(retriever, image_summaries, images)

    return retriever


# The vectorstore to use to index the summaries
vectorstore = Chroma(
    collection_name="mm_rag_cj_blog", embedding_function=OpenaiEmbeddings(client=get_openai().client)
)
retriever_multi_vector_img =  asyncio.run(create_multi_vector_retriever(
    vectorstore,
    text_summaries,
    texts,
    table_summaries,
    None,
    image_summaries,
    img_base64_list,
))

query = "Give me company names that are interesting investments based on EV / NTM and NTM rev growth. Consider EV / NTM multiples vs historical?"
docs = asyncio.run(retriever_multi_vector_img._get_relevant_documents(query))

# We get 4 docs
print(len(docs))



# from unstructured.partition.pdf import partition_pdf
import base64
import io
import re
import uuid
from PIL import Image
import os
from src.autobots.conn.chroma.chroma import Chroma, Document
from src.autobots.conn.chroma.multi_vector import MultiVectorRetriever, BaseStore
from src.autobots.conn.openai.openai_embeddings.openai_embeddings import OpenaiEmbeddings
from src.autobots.datastore.data_provider import DataProvider
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import asyncio
from fastapi import UploadFile
from src.autobots.conn.openai.openai_client import get_openai
import unstructured_client
from unstructured_client.models import operations, shared
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
        # print(element)
        if element["type"] == "Image":
            name= uuid.uuid4()
            with open(str(name)+".jpg", 'wb') as file:
                file.write(base64.b64decode(element["metadata"]["image_base64"]))
        if element["type"] == "Table":
            tables.append(element["metadata"]["text_as_html"])
        if element["type"] in ["NarrativeText",'UncategorizedText']:
            texts.append(element["text"])


    return texts, tables


# File path
fpath = "/Users/khushalsethi/godelsales/autobots/tests/resources/datastore/cj"
fname = "cj.pdf"
file_name = "tests/resources/datastore/cj/cj.pdf"


s3 = get_s3()
pinecone = get_pinecone()
unstructured = get_unstructured_io()
# Get elements
# raw_pdf_elements = extract_pdf_elements(fpath, fname)

s = unstructured_client.UnstructuredClient(
    api_key_auth=SettingsProvider.sget().UNSTRUCTURED_API_KEY,
)
with open(file_name, mode='rb') as file:
    upload_file = UploadFile(filename=file_name, file=file)
    req = shared.PartitionParameters(
        files=shared.Files(
                content=asyncio.run(upload_file.read()),
                file_name=file_name,
            ),
        strategy="hi_res",
        languages=["eng"],
        extract_image_block_types=["Image"]
)


raw_pdf_elements = s.general.partition(request=req
)

# # Get text, tables
texts, tables = categorize_elements(raw_pdf_elements.elements)

joined_texts = " ".join(texts)

# texts=["In an era dominated by screens and digital content, the simple act of reading a book may seem quaint or even obsolete. Yet, the intrinsic value of books has endured throughout centuries, transcending the rapid changes in technology and lifestyle. Reading books is not just a leisure activity; it is a multifaceted endeavor that offers profound benefits for our cognitive abilities, emotional health, and social skills. This essay delves into the myriad advantages of reading, underscoring its importance in our increasingly digital world."]
# # Optional: Enforce a specific token size for texts
async def get_texts_4k(joined_texts):
    texts=[]
    texts_4k_token_agen = DataProvider.create_data_chunks(joined_texts, DataProvider.read_data_line_by_line,4000
    )
    async for text in texts_4k_token_agen:
        texts.append(text)
    return texts

texts_4k_token = asyncio.run(get_texts_4k(joined_texts))
# texts_4k_token =texts

def encode_image(image_path):
    """Getting the base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def image_summarize(img_base64, prompt):
    """Make image summary"""

    response = client.chat.completions.create(model="gpt-4-vision-preview",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content":[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}]}
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
    tables,
    image_summaries,
    img_base64_list,
))

query = "Give me company names that are interesting investments based on EV / NTM and NTM rev growth. Consider EV / NTM multiples vs historical?"
docs = asyncio.run(retriever_multi_vector_img._get_relevant_documents(query))

# We get 4 docs
print(len(docs))


def resize_base64_image(base64_string, size=(128, 128)):
    """
    Resize an image encoded as a Base64 string
    """
    # Decode the Base64 string
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))

    # Resize the image
    resized_img = img.resize(size, Image.LANCZOS)

    # Save the resized image to a bytes buffer
    buffered = io.BytesIO()
    resized_img.save(buffered, format=img.format)

    # Encode the resized image to Base64
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def looks_like_base64(sb):
    """Check if the string looks like base64"""
    return re.match("^[A-Za-z0-9+/]+[=]{0,2}$", sb) is not None


def is_image_data(b64data):
    """
    Check if the base64 data is an image by looking at the start of the data
    """
    image_signatures = {
        b"\xff\xd8\xff": "jpg",
        b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": "png",
        b"\x47\x49\x46\x38": "gif",
        b"\x52\x49\x46\x46": "webp",
    }
    try:
        header = base64.b64decode(b64data)[:8]  # Decode and get the first 8 bytes
        for sig, format in image_signatures.items():
            if header.startswith(sig):
                return True
        return False
    except Exception:
        return False
    
def split_image_text_types(docs):
    """
    Split base64-encoded images and texts
    """
    b64_images = []
    texts = []
    for doc in docs:
        # Check if the document is of type Document and extract page_content if so
        if isinstance(doc, Document):
            doc = doc.page_content
        if looks_like_base64(doc) and is_image_data(doc):
            doc = resize_base64_image(doc, size=(1300, 600))
            b64_images.append(doc)
        else:
            texts.append(doc)
    return {"images": b64_images, "texts": texts}


def img_prompt_func(data_dict):
    """
    Join the context into a single string
    """
    formatted_texts = "\n".join(data_dict["context"]["texts"])
    messages = []

    # Adding image(s) to the messages if present
    if data_dict["context"]["images"]:
        for image in data_dict["context"]["images"]:
            image_message = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image}"},
            }
            messages.append(image_message)

    # Adding the text for analysis
    text_message = {
        "type": "text",
        "text": (
            "You are financial analyst tasking with providing investment advice.\n"
            "You will be given a mixed of text, tables, and image(s) usually of charts or graphs.\n"
            "Use this information to provide investment advice related to the user question. \n"
            f"User-provided question: {data_dict['question']}\n\n"
            "Text and / or tables:\n"
            f"{formatted_texts}"
        ),
    }
    messages.append(text_message)
    return messages

# chain = (
#         {
#             "context": retriever | RunnableLambda(split_image_text_types),
#             "question": RunnablePassthrough(),
#         }
#         | RunnableLambda(img_prompt_func)
#         | model
# chain_multimodal_rag.invoke(query)


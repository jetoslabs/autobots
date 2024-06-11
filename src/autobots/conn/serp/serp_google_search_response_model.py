from typing import Optional, List, Dict

from pydantic import BaseModel, HttpUrl


class SearchMetadata(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    json_endpoint: Optional[HttpUrl] = None
    created_at: Optional[str] = None
    processed_at: Optional[str] = None
    google_url: Optional[HttpUrl] = None
    raw_html_file: Optional[HttpUrl] = None
    total_time_taken: Optional[float] = None


class SearchParameters(BaseModel):
    device: Optional[str] = None
    engine: Optional[str] = None
    google_domain: Optional[str] = None
    q: Optional[str] = None


class SearchInformation(BaseModel):
    organic_results_state: Optional[str] = None
    query_displayed: Optional[str] = None
    time_taken_displayed: Optional[float] = None
    total_results: Optional[int] = None


class Sitelink(BaseModel):
    title: Optional[str] = None
    link: Optional[HttpUrl] = None


class Ad(BaseModel):
    position: Optional[int] = None
    block_position: Optional[str] = None
    title: Optional[str] = None
    link: Optional[HttpUrl] = None
    displayed_link: Optional[str] = None
    tracking_link: Optional[HttpUrl] = None
    description: Optional[str] = None
    source: Optional[str] = None
    sitelinks: Optional[List[Sitelink]] = None


class ShoppingResult(BaseModel):
    position: Optional[int] = None
    block_position: Optional[str] = None
    title: Optional[str] = None
    price: Optional[str] = None
    extracted_price: Optional[float] = None
    old_price: Optional[str] = None
    extracted_old_price: Optional[float] = None
    link: Optional[HttpUrl] = None
    product_link: Optional[HttpUrl] = None
    product_id: Optional[str] = None
    serpapi_product_api: Optional[HttpUrl] = None
    number_of_comparisons: Optional[str] = None
    comparison_link: Optional[HttpUrl] = None
    serpapi_product_api_comparisons: Optional[HttpUrl] = None
    source: Optional[str] = None
    shipping: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    thumbnail: Optional[HttpUrl] = None
    extensions: Optional[List[str]] = None
    badge: Optional[str] = None
    tag: Optional[str] = None
    delivery: Optional[str] = None
    store_rating: Optional[float] = None
    store_reviews: Optional[int] = None
    remark: Optional[str] = None


class ImmersiveProduct(BaseModel):
    thumbnail: Optional[str] = None
    source: Optional[str] = None
    title: Optional[str] = None
    price: Optional[str] = None
    extracted_price: Optional[float] = None
    original_price: Optional[str] = None
    extracted_original_price: Optional[float] = None
    extensions: Optional[List[str]] = None
    immersive_product_page_token: Optional[str] = None
    serpapi_link: Optional[str] = None


class RelatedQuestion(BaseModel):
    question: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None
    link: Optional[HttpUrl] = None
    list: Optional[List[str]] = None
    displayed_link: Optional[str] = None
    thumbnail: Optional[HttpUrl] = None
    source_logo: Optional[HttpUrl] = None
    next_page_token: Optional[str] = None
    serpapi_link: Optional[HttpUrl] = None


class Question(BaseModel):
    topic: Optional[str] = None
    question: Optional[str] = None
    link: Optional[HttpUrl] = None
    title: Optional[str] = None
    displayed_link: Optional[str] = None
    snippet: Optional[str] = None
    date: Optional[str] = None


class BuyingGuide(BaseModel):
    title: Optional[str] = None
    questions: Optional[List[Question]] = None


class InlineSitelink(BaseModel):
    title: Optional[str] = None
    link: Optional[HttpUrl] = None


class Sitelinks(BaseModel):
    inline: Optional[List[InlineSitelink]] = None


class DetectedExtensions(BaseModel):
    store_rating: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    free: Optional[int] = None


class TopRichSnippet(BaseModel):
    detected_extensions: Optional[DetectedExtensions] = None
    extensions: Optional[List[str]] = None


class RichSnippet(BaseModel):
    top: Optional[TopRichSnippet] = None


class OrganicResult(BaseModel):
    position: Optional[int] = None
    title: Optional[str] = None
    link: Optional[HttpUrl] = None
    redirect_link: Optional[HttpUrl] = None
    displayed_link: Optional[str] = None
    thumbnail: Optional[HttpUrl] = None
    favicon: Optional[HttpUrl] = None
    snippet: Optional[str] = None
    snippet_highlighted_words: Optional[List[str]] = None
    images: Optional[List[HttpUrl]] = None
    sitelinks: Optional[Sitelinks] = None
    rich_snippet: Optional[RichSnippet] = None
    source: Optional[str] = None


class RelatedSearch(BaseModel):
    block_position: Optional[int] = None
    query: Optional[str] = None
    link: Optional[HttpUrl] = None
    serpapi_link: Optional[HttpUrl] = None


class NewsResult(BaseModel):
    position: Optional[int] = None
    title: Optional[str] = None
    link: Optional[HttpUrl] = None
    source: Optional[str] = None
    date: Optional[str] = None
    snippet: Optional[str] = None
    thumbnail: Optional[str] = None


class RefineThisSearchItem(BaseModel):
    query: Optional[str] = None
    link: Optional[HttpUrl] = None
    serpapi_link: Optional[HttpUrl] = None
    thumbnail: Optional[HttpUrl] = None


class RefineThisSearch(BaseModel):
    items: List[RefineThisSearchItem] = None


class Filter(BaseModel):
    title: Optional[str]
    thumbnail: Optional[HttpUrl]
    link: Optional[HttpUrl]
    serpapi_link: Optional[HttpUrl]


class Category(BaseModel):
    title: Optional[str] = None
    filters: Optional[List[Filter]] = None


class Pagination(BaseModel):
    current: Optional[int] = None
    next: Optional[HttpUrl] = None
    other_pages: Optional[Dict[str, HttpUrl]] = None


class SerpapiPagination(BaseModel):
    current: Optional[int] = None
    next_link: Optional[HttpUrl] = None
    next: Optional[HttpUrl] = None
    other_pages: Optional[Dict[str, HttpUrl]] = None


class SearchResponse(BaseModel):
    search_metadata: Optional[SearchMetadata] = None
    search_parameters: Optional[SearchParameters] = None
    search_information: Optional[SearchInformation] = None
    ads: Optional[List[Ad]] = None
    inline_shopping_results: Optional[List[ShoppingResult]] = None
    shopping_results: Optional[List[ShoppingResult]] = None
    related_shopping_results: Optional[List[ShoppingResult]] = None
    featured_shopping_results: Optional[List[ShoppingResult]] = None
    inline_immersive_products: Optional[List[ImmersiveProduct]] = None
    immersive_products: Optional[List[ImmersiveProduct]] = None
    related_questions: Optional[List[RelatedQuestion]] = None
    buying_guide: Optional[BuyingGuide] = None
    organic_results: Optional[List[OrganicResult]] = None
    related_searches: Optional[List[RelatedSearch]] = None
    news_results: Optional[List[NewsResult]] = None
    refine_this_search: Optional[List[RefineThisSearch]] = None
    categories: Optional[List[Category]] = None
    pagination: Optional[Pagination] = None
    serpapi_pagination: Optional[SerpapiPagination] = None

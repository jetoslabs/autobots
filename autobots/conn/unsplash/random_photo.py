from typing import List, Optional
from pydantic import BaseModel


class UserLinks(BaseModel):
    self: str
    html: str
    photos: str
    likes: str
    portfolio: str
    following: str
    followers: str


class ProfileImage(BaseModel):
    small: str
    medium: str
    large: str


class Social(BaseModel):
    instagram_username: Optional[str]
    portfolio_url: Optional[str]
    twitter_username: Optional[str]
    paypal_email: Optional[str]


class User(BaseModel):
    id: str
    updated_at: str
    username: str
    name: str
    first_name: str
    last_name: Optional[str]
    twitter_username: Optional[str]
    portfolio_url: Optional[str]
    bio: Optional[str]
    location: Optional[str]
    links: UserLinks
    profile_image: ProfileImage
    instagram_username: str
    total_collections: int
    total_likes: int
    total_photos: int
    accepted_tos: bool
    for_hire: bool
    social: Optional[Social]


class Urls(BaseModel):
    raw: str
    full: str
    regular: str
    small: str
    thumb: str
    small_s3: str


class Links(BaseModel):
    self: str
    html: str
    download: str
    download_location: str


class Position(BaseModel):
    latitude: float
    longitude: float


class Location(BaseModel):
    name: Optional[str]
    city: Optional[str]
    country: Optional[str]
    position: Optional[Position]


class Exif(BaseModel):
    make: Optional[str]
    model: Optional[str]
    exposure_time: Optional[str]
    aperture: Optional[str]
    focal_length: Optional[str]
    iso: Optional[str]
    name: Optional[str]


class Image(BaseModel):
    id: str
    slug: str
    created_at: str
    updated_at: str
    promoted_at: str
    width: int
    height: int
    color: str
    blur_hash: str
    description: Optional[str]
    alt_description: str
    urls: Urls
    links: Links
    # likes: int
    # liked_by_user: bool
    # current_user_collections: List[str]
    # sponsorship: Optional[str]
    # topic_submissions: dict
    # user: User
    # exif: Exif
    # location: Location
    # views: int
    # downloads: int


class ImageList(BaseModel):
    __root__: List[Image]

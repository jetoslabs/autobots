from pydantic import BaseModel, Field


class ClaidConfig(BaseModel):
    claid_apikey: str = Field(description="Claid apikey used for request authorization.")
    claid_url: str = Field(default="http://api.claid.ai", description="Claid URL used for request "
                                                                      "authorization.")
    claid_side_s3_bucket: str
    https_path_s3_bucket: str
    claid_side_folder_url_prefix: str


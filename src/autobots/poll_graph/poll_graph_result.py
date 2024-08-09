from typing import Optional
from pydantic import BaseModel

class PollGraphResultDoc(BaseModel):
    id: str
    poll_graph_id: str
    result_data: dict  # Adjust the type as necessary for your result data structure
    created_at: str  # Use a proper date-time type if needed
    updated_at: str  # Use a proper date-time type if needed

class UserPollGraphResult(BaseModel):
    user_id: str
    poll_graph_result: PollGraphResultDoc
    status: str  # e.g., "pending", "completed", "failed"
    error_message: Optional[str] = None  # Optional field for error messages
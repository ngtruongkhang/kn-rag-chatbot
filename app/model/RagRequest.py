from typing import List

from pydantic import BaseModel

class RagRequest(BaseModel):
    kb_name: str
    user_input: str
    conversation_id: str
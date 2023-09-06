from pydantic import BaseModel


class NewsCrawler(BaseModel):
    session_id: int
    status: str = None

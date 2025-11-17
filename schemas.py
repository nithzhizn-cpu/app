from pydantic import BaseModel

class PubKeyUpdate(BaseModel):
    pubkey: str
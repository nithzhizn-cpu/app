from pydantic import BaseModel

class RegisterRequest(BaseModel):
    username: str
    telegram_id: str | None = None

class UserOut(BaseModel):
    id: int
    username: str

class PubKeyUpdate(BaseModel):
    pubkey: str

class PubKeyOut(BaseModel):
    pubkey: str

class MessageCreate(BaseModel):
    to: int
    iv: str
    ciphertext: str
    msg_type: str | None = None
    ttl_sec: int | None = None

class MessageOut(BaseModel):
    id: int
    from_id: int
    to_id: int
    iv: str
    ciphertext: str

class MessagesResponse(BaseModel):
    messages: list[MessageOut]

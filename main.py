from fastapi import FastAPI, Depends, HTTPException, Header, Query
from app.models import Base, User, Message
from app.schemas import *
from app.database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SpySignal Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(401, "Missing Authorization")

    token = authorization.replace("Bearer ", "")
    user = db.query(User).filter(User.token == token).first()

    if not user:
        raise HTTPException(401, "Invalid token")

    return user


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        return {"id": existing.id, "username": existing.username, "token": existing.token}

    token = secrets.token_hex(32)
    user = User(username=req.username, telegram_id=req.telegram_id, token=token)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "username": user.username, "token": user.token}


@app.get("/api/users/search")
def search_users(query: str, db: Session = Depends(get_db)):
    results = []

    if query.isdigit():
        u = db.query(User).filter(User.id == int(query)).first()
        if u:
            results.append(u)

    by_name = db.query(User).filter(User.username.ilike(f"%{query}%")).all()

    for u in by_name:
        if u not in results:
            results.append(u)

    return {"results": [{"id": u.id, "username": u.username} for u in results]}


@app.post("/api/pubkey")
def save_pubkey(req: PubKeyUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    user.pubkey = req.pubkey
    db.commit()
    return {"ok": True}


@app.get("/api/pubkey/{user_id}")
def get_pubkey(user_id: int, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u or not u.pubkey:
        raise HTTPException(404, "No pubkey")
    return {"pubkey": u.pubkey}


@app.post("/api/messages")
def new_msg(msg: MessageCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    m = Message(
        from_id=user.id,
        to_id=msg.to,
        iv=msg.iv,
        ciphertext=msg.ciphertext,
        msg_type=msg.msg_type,
        ttl_sec=msg.ttl_sec,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"ok": True, "id": m.id}


@app.get("/api/messages")
def get_messages(peer_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    msgs = db.query(Message).filter(
        ((Message.from_id == user.id) & (Message.to_id == peer_id)) |
        ((Message.from_id == peer_id) & (Message.to_id == user.id))
    ).order_by(Message.created_at.asc())

    visible = []
    for m in msgs:
        if m.ttl_sec:
            if m.created_at + timedelta(seconds=m.ttl_sec) < now:
                continue
        visible.append(m)

    return {"messages": visible}

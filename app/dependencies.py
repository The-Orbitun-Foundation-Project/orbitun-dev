from fastapi import Depends, HTTPException, Header
from sqlmodel import SQLModel, create_engine, Session, select
from dotenv import load_dotenv
import os

from .models.tenant_api_keys import TenantApiKey

# Database setup                                                                             
load_dotenv()  # Load environment variables from .env

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")
engine = create_engine(DATABASE_URL, echo=True)

# Database utilities
def get_session():
    with Session(engine) as session:
        yield session

# Resolve the X-API-Key header to the owning tenant's ID
def get_current_tenant_id(
    x_api_key: str = Header(...),
    session: Session = Depends(get_session),
) -> int:
    api_key = session.exec(
        select(TenantApiKey).where(TenantApiKey.key == x_api_key)
    ).first()
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key.tenant_id

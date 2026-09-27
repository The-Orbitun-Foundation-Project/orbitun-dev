from sqlmodel import SQLModel, Field, Relationship
from ..schemas.tenants import TenantInput
from .agents import Agent

class Tenant(TenantInput, table=True):
    __tablename__="tenants"
    id : int = Field(primary_key = True, default=None)
    
    policies: list["Policy"] = Relationship(back_populates="tenant")
    agents: list["Agent"] = Relationship(back_populates="tenant")
    api_keys: list["TenantApiKey"] = Relationship(back_populates="tenant", cascade_delete=True)


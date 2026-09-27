from sqlmodel import Field, Relationship
from ..schemas.tenant_api_keys import TenantApiKeyInput
from .tenants import Tenant

class TenantApiKey(TenantApiKeyInput, table=True):
    __tablename__="tenant_api_keys"
    id : int = Field(primary_key = True, default=None)
    tenant_id : int = Field(foreign_key="tenants.id")

    tenant: Tenant = Relationship(back_populates="api_keys")

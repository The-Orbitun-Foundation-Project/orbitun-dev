from sqlmodel import SQLModel, Field

class TenantApiKeyInput(SQLModel):
    key: str = Field(unique=True, index=True)
    label: str | None = None

class TenantApiKeyOutput(TenantApiKeyInput):
    id: int
    tenant_id: int

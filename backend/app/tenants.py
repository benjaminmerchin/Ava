"""Per-tenant configuration. Ava is multi-tenant-ready; for the demo we
onboard exactly one tenant (Lyvica)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TenantConfig:
    id: str
    name: str
    language: str = "fr"
    selector_attr: str = "data-ava"  # preferred stable selector attribute


_TENANTS: dict[str, TenantConfig] = {
    "lyvica": TenantConfig(id="lyvica", name="Lyvica", language="fr"),
}


def get_tenant(tenant_id: str) -> TenantConfig:
    return _TENANTS.get(tenant_id, _TENANTS["lyvica"])

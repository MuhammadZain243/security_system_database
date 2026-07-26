"""Seed data definitions for stable database bootstrap data."""

from security_system_database.seeds.platform_rbac import (
    PLATFORM_PERMISSIONS,
    PLATFORM_ROLES,
    PlatformPermissionSeed,
    PlatformRoleSeed,
)

__all__ = [
    "PLATFORM_PERMISSIONS",
    "PLATFORM_ROLES",
    "PlatformPermissionSeed",
    "PlatformRoleSeed",
]

"""Initial platform RBAC seed data."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformPermissionSeed:
    """Stable platform permission seed definition."""

    key: str
    name: str
    category: str
    description: str


@dataclass(frozen=True)
class PlatformRoleSeed:
    """Stable platform role seed definition."""

    slug: str
    name: str
    description: str
    is_system: bool
    permission_keys: tuple[str, ...]


PLATFORM_PERMISSIONS: tuple[PlatformPermissionSeed, ...] = (
    PlatformPermissionSeed(
        key="platform.users.read",
        name="View Platform Users",
        category="platform.users",
        description="View internal platform users.",
    ),
    PlatformPermissionSeed(
        key="platform.users.create",
        name="Create Platform Users",
        category="platform.users",
        description="Create internal platform users.",
    ),
    PlatformPermissionSeed(
        key="platform.users.update",
        name="Update Platform Users",
        category="platform.users",
        description="Update internal platform users.",
    ),
    PlatformPermissionSeed(
        key="platform.users.delete",
        name="Delete Platform Users",
        category="platform.users",
        description="Delete or deactivate internal platform users.",
    ),
    PlatformPermissionSeed(
        key="platform.roles.read",
        name="View Platform Roles",
        category="platform.roles",
        description="View platform roles and permission assignments.",
    ),
    PlatformPermissionSeed(
        key="platform.roles.create",
        name="Create Platform Roles",
        category="platform.roles",
        description="Create platform roles.",
    ),
    PlatformPermissionSeed(
        key="platform.roles.update",
        name="Update Platform Roles",
        category="platform.roles",
        description="Update platform roles and permission assignments.",
    ),
    PlatformPermissionSeed(
        key="platform.roles.delete",
        name="Delete Platform Roles",
        category="platform.roles",
        description="Delete platform roles.",
    ),
    PlatformPermissionSeed(
        key="platform.companies.read",
        name="View Companies",
        category="platform.companies",
        description="View customer companies.",
    ),
    PlatformPermissionSeed(
        key="platform.companies.create",
        name="Create Companies",
        category="platform.companies",
        description="Create customer companies.",
    ),
    PlatformPermissionSeed(
        key="platform.companies.update",
        name="Update Companies",
        category="platform.companies",
        description="Update customer company records.",
    ),
    PlatformPermissionSeed(
        key="platform.companies.suspend",
        name="Suspend Companies",
        category="platform.companies",
        description="Suspend or reactivate customer companies.",
    ),
    PlatformPermissionSeed(
        key="platform.companies.delete",
        name="Delete Companies",
        category="platform.companies",
        description="Delete customer company records.",
    ),
    PlatformPermissionSeed(
        key="platform.configuration.read",
        name="View Platform Configuration",
        category="platform.configuration",
        description="View platform-managed configuration and integrations.",
    ),
    PlatformPermissionSeed(
        key="platform.configuration.update",
        name="Update Platform Configuration",
        category="platform.configuration",
        description="Update platform-managed configuration and integrations.",
    ),
    PlatformPermissionSeed(
        key="platform.configuration.connect",
        name="Connect Platform Integrations",
        category="platform.configuration",
        description="Connect third-party integrations such as Google OAuth.",
    ),
    PlatformPermissionSeed(
        key="platform.configuration.disconnect",
        name="Disconnect Platform Integrations",
        category="platform.configuration",
        description="Disconnect third-party integrations.",
    ),
)

_ALL_PLATFORM_PERMISSION_KEYS = tuple(
    permission.key for permission in PLATFORM_PERMISSIONS
)

PLATFORM_ROLES: tuple[PlatformRoleSeed, ...] = (
    PlatformRoleSeed(
        slug="super-admin",
        name="Super Admin",
        description="Full platform owner access.",
        is_system=True,
        permission_keys=_ALL_PLATFORM_PERMISSION_KEYS,
    ),
    PlatformRoleSeed(
        slug="platform-admin",
        name="Platform Admin",
        description="Broad platform management access.",
        is_system=True,
        permission_keys=_ALL_PLATFORM_PERMISSION_KEYS,
    ),
    PlatformRoleSeed(
        slug="hr-manager",
        name="HR Manager",
        description="Manages internal platform users.",
        is_system=True,
        permission_keys=(
            "platform.users.read",
            "platform.users.create",
            "platform.users.update",
            "platform.users.delete",
            "platform.roles.read",
        ),
    ),
    PlatformRoleSeed(
        slug="support-agent",
        name="Support Agent",
        description="Limited read access for platform support.",
        is_system=True,
        permission_keys=(
            "platform.users.read",
            "platform.roles.read",
            "platform.companies.read",
            "platform.configuration.read",
        ),
    ),
    PlatformRoleSeed(
        slug="company-manager",
        name="Company Manager",
        description="Manages customer company records.",
        is_system=True,
        permission_keys=(
            "platform.companies.read",
            "platform.companies.create",
            "platform.companies.update",
            "platform.companies.suspend",
        ),
    ),
)

"""seed initial platform rbac data

Revision ID: c6f7114a7e29
Revises: 47d5622504b3
Create Date: 2026-07-26 15:42:58.996456

"""

from collections.abc import Sequence
from uuid import NAMESPACE_URL, uuid5

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c6f7114a7e29"
down_revision: str | Sequence[str] | None = "47d5622504b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PLATFORM_PERMISSIONS = (
    {
        "key": "platform.users.read",
        "name": "View Platform Users",
        "category": "platform.users",
        "description": "View internal platform users.",
    },
    {
        "key": "platform.users.create",
        "name": "Create Platform Users",
        "category": "platform.users",
        "description": "Create internal platform users.",
    },
    {
        "key": "platform.users.update",
        "name": "Update Platform Users",
        "category": "platform.users",
        "description": "Update internal platform users.",
    },
    {
        "key": "platform.users.delete",
        "name": "Delete Platform Users",
        "category": "platform.users",
        "description": "Delete or deactivate internal platform users.",
    },
    {
        "key": "platform.roles.read",
        "name": "View Platform Roles",
        "category": "platform.roles",
        "description": "View platform roles and permission assignments.",
    },
    {
        "key": "platform.roles.create",
        "name": "Create Platform Roles",
        "category": "platform.roles",
        "description": "Create platform roles.",
    },
    {
        "key": "platform.roles.update",
        "name": "Update Platform Roles",
        "category": "platform.roles",
        "description": "Update platform roles and permission assignments.",
    },
    {
        "key": "platform.roles.delete",
        "name": "Delete Platform Roles",
        "category": "platform.roles",
        "description": "Delete platform roles.",
    },
    {
        "key": "platform.companies.read",
        "name": "View Companies",
        "category": "platform.companies",
        "description": "View customer companies.",
    },
    {
        "key": "platform.companies.create",
        "name": "Create Companies",
        "category": "platform.companies",
        "description": "Create customer companies.",
    },
    {
        "key": "platform.companies.update",
        "name": "Update Companies",
        "category": "platform.companies",
        "description": "Update customer company records.",
    },
    {
        "key": "platform.companies.suspend",
        "name": "Suspend Companies",
        "category": "platform.companies",
        "description": "Suspend or reactivate customer companies.",
    },
    {
        "key": "platform.companies.delete",
        "name": "Delete Companies",
        "category": "platform.companies",
        "description": "Delete customer company records.",
    },
    {
        "key": "platform.configuration.read",
        "name": "View Platform Configuration",
        "category": "platform.configuration",
        "description": "View platform-managed configuration and integrations.",
    },
    {
        "key": "platform.configuration.update",
        "name": "Update Platform Configuration",
        "category": "platform.configuration",
        "description": "Update platform-managed configuration and integrations.",
    },
    {
        "key": "platform.configuration.connect",
        "name": "Connect Platform Integrations",
        "category": "platform.configuration",
        "description": "Connect third-party integrations such as Google OAuth.",
    },
    {
        "key": "platform.configuration.disconnect",
        "name": "Disconnect Platform Integrations",
        "category": "platform.configuration",
        "description": "Disconnect third-party integrations.",
    },
)

ALL_PERMISSION_KEYS = tuple(permission["key"] for permission in PLATFORM_PERMISSIONS)

PLATFORM_ROLES = (
    {
        "slug": "super-admin",
        "name": "Super Admin",
        "description": "Full platform owner access.",
        "is_system": True,
        "permission_keys": ALL_PERMISSION_KEYS,
    },
    {
        "slug": "platform-admin",
        "name": "Platform Admin",
        "description": "Broad platform management access.",
        "is_system": True,
        "permission_keys": ALL_PERMISSION_KEYS,
    },
    {
        "slug": "hr-manager",
        "name": "HR Manager",
        "description": "Manages internal platform users.",
        "is_system": True,
        "permission_keys": (
            "platform.users.read",
            "platform.users.create",
            "platform.users.update",
            "platform.users.delete",
            "platform.roles.read",
        ),
    },
    {
        "slug": "support-agent",
        "name": "Support Agent",
        "description": "Limited read access for platform support.",
        "is_system": True,
        "permission_keys": (
            "platform.users.read",
            "platform.roles.read",
            "platform.companies.read",
            "platform.configuration.read",
        ),
    },
    {
        "slug": "company-manager",
        "name": "Company Manager",
        "description": "Manages customer company records.",
        "is_system": True,
        "permission_keys": (
            "platform.companies.read",
            "platform.companies.create",
            "platform.companies.update",
            "platform.companies.suspend",
        ),
    },
)


def _seed_uuid(kind: str, value: str) -> str:
    return str(
        uuid5(
            NAMESPACE_URL,
            f"https://security-system.local/seed/platform-rbac/{kind}/{value}",
        )
    )


def upgrade() -> None:
    """Upgrade schema."""

    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            INSERT INTO platform_permissions (
                id,
                key,
                name,
                description,
                category,
                created_at,
                updated_at
            )
            VALUES (
                :id,
                :key,
                :name,
                :description,
                :category,
                now(),
                now()
            )
            ON CONFLICT (key) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                category = EXCLUDED.category,
                updated_at = now()
            """
        ),
        [
            {
                **permission,
                "id": _seed_uuid("permission", permission["key"]),
            }
            for permission in PLATFORM_PERMISSIONS
        ],
    )

    connection.execute(
        sa.text(
            """
            INSERT INTO platform_roles (
                id,
                name,
                slug,
                description,
                is_system,
                created_at,
                updated_at
            )
            VALUES (
                :id,
                :name,
                :slug,
                :description,
                :is_system,
                now(),
                now()
            )
            ON CONFLICT (slug) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                is_system = EXCLUDED.is_system,
                updated_at = now()
            """
        ),
        [
            {
                "id": _seed_uuid("role", role["slug"]),
                "name": role["name"],
                "slug": role["slug"],
                "description": role["description"],
                "is_system": role["is_system"],
            }
            for role in PLATFORM_ROLES
        ],
    )

    role_permission_insert = sa.text(
        """
        INSERT INTO platform_role_permissions (
            id,
            platform_role_id,
            platform_permission_id,
            created_at
        )
        SELECT
            :id,
            platform_roles.id,
            platform_permissions.id,
            now()
        FROM platform_roles, platform_permissions
        WHERE platform_roles.slug = :role_slug
          AND platform_permissions.key = :permission_key
        ON CONFLICT (
            platform_role_id,
            platform_permission_id
        ) DO NOTHING
        """
    )
    role_permission_rows = [
        {
            "id": _seed_uuid(
                "role-permission",
                f"{role['slug']}:{permission_key}",
            ),
            "role_slug": role["slug"],
            "permission_key": permission_key,
        }
        for role in PLATFORM_ROLES
        for permission_key in role["permission_keys"]
    ]

    connection.execute(role_permission_insert, role_permission_rows)


def downgrade() -> None:
    """Downgrade schema."""

    connection = op.get_bind()

    for role in PLATFORM_ROLES:
        for permission_key in role["permission_keys"]:
            connection.execute(
                sa.text(
                    """
                    DELETE FROM platform_role_permissions
                    WHERE platform_role_id = (
                        SELECT id FROM platform_roles WHERE slug = :role_slug
                    )
                    AND platform_permission_id = (
                        SELECT id FROM platform_permissions WHERE key = :permission_key
                    )
                    """
                ),
                {
                    "role_slug": role["slug"],
                    "permission_key": permission_key,
                },
            )

    for role in PLATFORM_ROLES:
        connection.execute(
            sa.text("DELETE FROM platform_roles WHERE slug = :slug"),
            {"slug": role["slug"]},
        )

    for permission in PLATFORM_PERMISSIONS:
        connection.execute(
            sa.text("DELETE FROM platform_permissions WHERE key = :key"),
            {"key": permission["key"]},
        )

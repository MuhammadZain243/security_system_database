"""Tests for initial platform RBAC seed data."""

from security_system_database.seeds.platform_rbac import (
    PLATFORM_PERMISSIONS,
    PLATFORM_ROLES,
)


def test_platform_permission_keys_are_unique() -> None:
    keys = [permission.key for permission in PLATFORM_PERMISSIONS]

    assert len(keys) == len(set(keys))


def test_platform_permission_keys_are_lowercase_dot_notation() -> None:
    for permission in PLATFORM_PERMISSIONS:
        assert permission.key == permission.key.lower()
        assert permission.key.startswith("platform.")
        assert permission.key.count(".") >= 2


def test_platform_permission_categories_match_key_prefixes() -> None:
    for permission in PLATFORM_PERMISSIONS:
        resource_prefix = ".".join(permission.key.split(".")[:2])

        assert permission.category == resource_prefix


def test_platform_configuration_permissions_are_seeded() -> None:
    keys = {permission.key for permission in PLATFORM_PERMISSIONS}

    assert "platform.configuration.read" in keys
    assert "platform.configuration.update" in keys
    assert "platform.configuration.connect" in keys
    assert "platform.configuration.disconnect" in keys


def test_platform_role_slugs_are_unique_and_lowercase() -> None:
    slugs = [role.slug for role in PLATFORM_ROLES]

    assert len(slugs) == len(set(slugs))
    for slug in slugs:
        assert slug == slug.lower()


def test_every_role_permission_references_known_permission_key() -> None:
    permission_keys = {permission.key for permission in PLATFORM_PERMISSIONS}

    for role in PLATFORM_ROLES:
        assert set(role.permission_keys).issubset(permission_keys)


def test_super_admin_role_includes_all_platform_permissions() -> None:
    permission_keys = {permission.key for permission in PLATFORM_PERMISSIONS}
    super_admin = next(
        (role for role in PLATFORM_ROLES if role.slug == "super-admin"),
        None,
    )

    assert super_admin is not None
    assert set(super_admin.permission_keys) == permission_keys


def test_no_seed_data_contains_secrets() -> None:
    seed_text = repr((PLATFORM_PERMISSIONS, PLATFORM_ROLES)).lower()

    assert "password" not in seed_text
    assert "secret" not in seed_text
    assert "token" not in seed_text

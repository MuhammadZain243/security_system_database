"""Basic package setup tests."""

from security_system_database import DatabaseSettings


def test_database_settings_build_psycopg_url() -> None:
    settings = DatabaseSettings(
        _env_file=None,
        host="localhost",
        port=5432,
        name="security_system",
        user="security_system",
        password="test-password",
        ssl_mode="disable",
    )

    url = settings.sqlalchemy_url

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "localhost"
    assert url.port == 5432
    assert url.database == "security_system"
    assert url.username == "security_system"
    assert url.password == "test-password"

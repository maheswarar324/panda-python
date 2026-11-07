import pytest

from panda.config.config_loader import load_config


def test_load_config_reads_application_properties():
    config = load_config()

    assert config.get("application", "name") == "PANDA"
    assert config.get("database", "type") == "sqlite"


def test_load_config_reads_environment_specific_properties():
    config = load_config()

    assert config.get("application", "environment") == "dev"
    assert config.get("database", "name") == "panda-dev.db"
    assert config.get("database", "type") == "sqlite"


def test_load_config_reads_correct_data_types():
    config = load_config()

    assert config.getint("database", "timeout") == 30
    assert config.getboolean("database", "foreign_keys") is True
    assert config.getboolean("database", "show_sql") is True


def test_load_config_uses_supplied_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("PANDA_ENV", "test")

    (tmp_path / "application.properties").write_text(
        "[application]\nname = PANDA-TEST\n",
        encoding="utf-8",
    )

    (tmp_path / "application-test.properties").write_text(
        "[database]\ntype = sqlite\n",
        encoding="utf-8",
    )

    config = load_config(config_directory=tmp_path)

    assert config.get("application", "name") == "PANDA-TEST"
    assert config.get("database", "type") == "sqlite"


def test_load_config_defaults_to_dev_environment(monkeypatch):
    monkeypatch.delenv("PANDA_ENV", raising=False)

    config = load_config()

    assert config.get("application", "environment") == "dev"
    assert config.get("database", "name") == "panda-dev.db"


def test_environment_specific_properties_override_application_properties(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("PANDA_ENV", "dev")

    (tmp_path / "application.properties").write_text(
        "[database]\ntype = sqlite\ntimeout = 30\n",
        encoding="utf-8",
    )

    (tmp_path / "application-dev.properties").write_text(
        "[database]\ntimeout = 60\n",
        encoding="utf-8",
    )

    config = load_config(config_directory=tmp_path)

    assert config.get("database", "type") == "sqlite"
    assert config.getint("database", "timeout") == 60


def test_load_config_raises_error_when_environment_file_is_missing(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("PANDA_ENV", "test")

    (tmp_path / "application.properties").write_text(
        "[application]\nname = PANDA\n",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError):
        load_config(config_directory=tmp_path)


def test_load_config_rejects_unsupported_environment(monkeypatch):
    monkeypatch.setenv("PANDA_ENV", "staging")

    with pytest.raises(ValueError):
        load_config()


def test_load_config_reads_production_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("PANDA_ENV", "prod")

    (tmp_path / "application.properties").write_text(
        "[application]\nname = PANDA\n",
        encoding="utf-8",
    )

    (tmp_path / "application-prod.properties").write_text(
        "[application]\nenvironment = prod\n[database]\nname = panda-prod.db\n",
        encoding="utf-8",
    )

    config = load_config(config_directory=tmp_path)

    assert config.get("application", "environment") == "prod"
    assert config.get("database", "name") == "panda-prod.db"

from panda.config.database_config import get_database_config


def test_get_database_config():
    database_config = get_database_config()

    assert database_config["type"] == "sqlite"
    assert database_config["timeout"] == 30
    assert database_config["foreign_keys"] is True
    assert database_config["name"] == "panda-dev.db"
    assert database_config["path"] == "./data/dev/panda-dev.db"
    assert database_config["show_sql"] is True

from panda.config.config_loader import load_config


def get_database_config():
    config = load_config()

    return {
        "type": config.get("database", "type"),
        "timeout": config.getint("database", "timeout"),
        "foreign_keys": config.getboolean("database", "foreign_keys"),
        "name": config.get("database", "name"),
        "path": config.get("database", "path"),
        "show_sql": config.getboolean("database", "show_sql"),
    }

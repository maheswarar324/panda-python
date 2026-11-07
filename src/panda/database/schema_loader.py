from panda.config.paths import SCHEMA_FILE


def load_schema() -> str:
    return SCHEMA_FILE.read_text(encoding="utf-8")

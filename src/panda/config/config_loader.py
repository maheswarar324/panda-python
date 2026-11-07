import configparser
import os
from pathlib import Path

from panda.config.paths import CONFIG_DIRECTORY

SUPPORTED_ENVIRONMENTS = {"dev", "test", "prod"}


def load_config(config_directory: Path = CONFIG_DIRECTORY):
    environment = os.getenv("PANDA_ENV", "dev")

    if environment not in SUPPORTED_ENVIRONMENTS:
        raise ValueError(
            f"Unsupported PANDA_ENV: '{environment}'. "
            f"Supported environments: {', '.join(sorted(SUPPORTED_ENVIRONMENTS))}"
        )

    config_path = Path(config_directory)

    application_config = config_path / "application.properties"
    environment_config = config_path / f"application-{environment}.properties"

    for config_file in (application_config, environment_config):
        if not config_file.is_file():
            raise FileNotFoundError(
                f"Required configuration file not found: {config_file}"
            )

    config = configparser.ConfigParser()

    config.read(
        [
            application_config,
            environment_config,
        ],
        encoding="utf-8",
    )

    return config

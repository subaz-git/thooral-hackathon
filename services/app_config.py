import copy
import json
import os

from services.config import CONFIG_FILE


DEFAULT_CONFIG = {
    "docs": {
        "default_format": "plain_text",
    },
    "confirmations": {
        "docs_delete": True,
        "sheets_clear": True,
    },
}


def _merge_dicts(base, override):
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_app_config():
    if not os.path.exists(CONFIG_FILE):
        return copy.deepcopy(DEFAULT_CONFIG), None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
            user_config = json.load(config_file)
        if not isinstance(user_config, dict):
            raise ValueError("config file must contain a JSON object.")
    except Exception as error:
        return (
            copy.deepcopy(DEFAULT_CONFIG),
            f"Failed to load config '{CONFIG_FILE}': {error}",
        )

    return _merge_dicts(DEFAULT_CONFIG, user_config), None


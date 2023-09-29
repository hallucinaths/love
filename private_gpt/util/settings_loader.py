import functools
import os
import sys
from pathlib import Path
from typing import Any

from pydantic.v1.utils import deep_update, unique_list

from private_gpt.constants import PROJECT_ROOT_PATH
from private_gpt.util.yaml import load_yaml_with_envvars

_settings_folder = os.environ.get("PGPT_SETTINGS_FOLDER", PROJECT_ROOT_PATH)

# if running in unittest, use the test profile
_test_profile = ["test"] if "unittest" in sys.modules else []

active_profiles: list[str] = unique_list(
    ["default"]
    + [
        item.strip()
        for item in os.environ.get("PGPT_PROFILES", "").split(",")
        if item.strip()
    ]
    + _test_profile
)


def load_profile(profile: str) -> dict[str, Any]:
    if profile == "default":
        profile_file_name = "settings.yaml"
    else:
        profile_file_name = f"settings-{profile}.yaml"

    path = Path(_settings_folder) / profile_file_name
    with Path(path).open("r") as f:
        config = load_yaml_with_envvars(f)
    if not isinstance(config, dict):
        raise TypeError(f"Config file has no top-level mapping: {path}")
    return config


def load_active_profiles() -> dict[str, Any]:
    """Load active profiles and merge them."""
    loaded_profiles = [load_profile(profile) for profile in active_profiles]
    merged: dict[str, Any] = functools.reduce(deep_update, loaded_profiles, {})
    return merged

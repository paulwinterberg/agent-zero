import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_GAME_DATA: Dict[str, Any] = {
    "has_played": True,
    "completed_levels": {},
}

RESET_DATA_EVERY_TIME = False

SAVE_FILE = (
    Path(__file__).resolve().parents[2] / "data" / "saves" / "game_save.json"
)


def _type_matches(default: Any, value: Any) -> bool:
    """Check value against the type of default (bool is not treated as int)."""
    if isinstance(default, bool):
        return isinstance(value, bool)
    if isinstance(default, int):
        return isinstance(value, int) and not isinstance(value, bool)
    if isinstance(default, float):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, type(default))


def _validate(default: Any, value: Any) -> Any:
    """Recursively build a value shaped like `default`, using `value` where valid."""
    # Nested schema: default dict with keys -> validate each key, drop unknowns
    if isinstance(default, dict) and default:
        if not isinstance(value, dict):
            return copy.deepcopy(default)
        return {key: _validate(sub_default, value.get(key, sub_default))
                for key, sub_default in default.items()}

    # Empty default dict = free-form mapping (e.g. completed_levels): keep contents
    if isinstance(default, dict):
        return copy.deepcopy(value) if isinstance(value, dict) else {}

    # Lists: keep if it's a list
    if isinstance(default, list):
        return copy.deepcopy(value) if isinstance(value, list) else copy.deepcopy(default)

    # Scalars: keep if type matches, otherwise fall back to default
    return value if _type_matches(default, value) else copy.deepcopy(default)


def _validated_data(data: Any) -> Dict[str, Any]:
    return _validate(DEFAULT_GAME_DATA, data)


def save_game_data(data: Dict[str, Any]) -> None:
    validated_data = _validated_data(data)
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SAVE_FILE.write_text(
        json.dumps(validated_data, indent=2) + "\n",
        encoding="utf-8",
    )


def reset_game_data() -> Dict[str, Any]:
    data = copy.deepcopy(DEFAULT_GAME_DATA)
    save_game_data(data)
    return data


def load_game_data(reset: Optional[bool] = None) -> Dict[str, Any]:
    if reset is None:
        reset = RESET_DATA_EVERY_TIME

    if reset or not SAVE_FILE.exists():
        return reset_game_data()

    try:
        with SAVE_FILE.open(encoding="utf-8") as save_file:
            return _validated_data(json.load(save_file))
    except (json.JSONDecodeError, OSError):
        return reset_game_data()
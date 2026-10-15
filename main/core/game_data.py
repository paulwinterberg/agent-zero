import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_GAME_DATA: Dict[str, bool] = {
    "has_played": True
}

RESET_DATA_EVERY_TIME = True

SAVE_FILE = (
    Path(__file__).resolve().parents[2] / "data" / "saves" / "game_save.json"
)

def _validated_data(data: Any) -> Dict[str, bool]:
    if (
        not isinstance(data, dict)
        or set(data) != set(DEFAULT_GAME_DATA)
        or type(data["has_played"]) is not bool
    ):
        raise ValueError("Game save data must contain a boolean 'has_played' value.")

    return {"has_played": data["has_played"]}


def save_game_data(data: Dict[str, bool]) -> None:
    validated_data = _validated_data(data)
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SAVE_FILE.write_text(
        json.dumps(validated_data, indent=2) + "\n",
        encoding="utf-8",
    )


def reset_game_data() -> Dict[str, bool]:
    data = DEFAULT_GAME_DATA.copy()
    save_game_data(data)
    return data


def load_game_data(reset: Optional[bool] = None) -> Dict[str, bool]:
    if reset is None:
        reset = RESET_DATA_EVERY_TIME

    if reset:
        return reset_game_data()

    if not SAVE_FILE.exists():
        return reset_game_data()

    with SAVE_FILE.open(encoding="utf-8") as save_file:
        return _validated_data(json.load(save_file))

"""Save/Load system for ENGI — SQLite + compressed flat file persistence."""

import json
import os
import pickle
import shutil
import sqlite3
import zlib
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Serialization helpers (module-level)
# ---------------------------------------------------------------------------


def serialize_chunk(chunk_data) -> bytes:
    """Pickle chunk_data and compress with zlib."""
    return zlib.compress(pickle.dumps(chunk_data, protocol=pickle.HIGHEST_PROTOCOL))


def deserialize_chunk(raw_bytes: bytes):
    """Decompress zlib bytes and unpickle to chunk_data."""
    return pickle.loads(zlib.decompress(raw_bytes))


# ---------------------------------------------------------------------------
# SQL schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS player_state (
    id INTEGER PRIMARY KEY DEFAULT 1,
    data TEXT
);
CREATE TABLE IF NOT EXISTS game_state (
    id INTEGER PRIMARY KEY DEFAULT 1,
    data TEXT
);
CREATE TABLE IF NOT EXISTS clan_states (
    clan_id TEXT PRIMARY KEY,
    data TEXT
);
CREATE TABLE IF NOT EXISTS explored_areas (
    region_col INTEGER,
    region_row INTEGER,
    area_x INTEGER,
    area_y INTEGER,
    modified INTEGER DEFAULT 0,
    explore_time TEXT,
    PRIMARY KEY (region_col, region_row, area_x, area_y)
);
CREATE TABLE IF NOT EXISTS npc_state (
    npc_id TEXT PRIMARY KEY,
    data TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn INTEGER,
    event_type TEXT,
    data TEXT
);
"""

_SAVE_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# SaveManager
# ---------------------------------------------------------------------------


class SaveManager:
    """Manages save/load operations using SQLite and compressed flat files."""

    def __init__(self, save_dir: str = "saves") -> None:
        self.save_dir = Path(save_dir)
        self._connections: dict[str, sqlite3.Connection] = {}

    # -- internal helpers ---------------------------------------------------

    def _slot_dir(self, slot: str) -> Path:
        return self.save_dir / slot

    def _db_path(self, slot: str) -> Path:
        return self._slot_dir(slot) / "save.db"

    def _get_conn(self, slot: str) -> sqlite3.Connection:
        """Return an open connection for *slot*, opening one if needed."""
        if slot not in self._connections:
            self.init_db(slot)
        return self._connections[slot]

    # -- public API ---------------------------------------------------------

    def init_db(self, slot: str) -> None:
        """Create / open the SQLite database for *slot* and ensure schema."""
        slot_dir = self._slot_dir(slot)
        slot_dir.mkdir(parents=True, exist_ok=True)

        db_path = self._db_path(slot)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        conn.executescript(_SCHEMA_SQL)
        conn.commit()
        self._connections[slot] = conn

    # -- game state ---------------------------------------------------------

    def save_game(
        self,
        slot: str,
        player_data: dict,
        game_state_data: dict,
        clan_states: dict,
        *,
        auto: bool = False,
    ) -> None:
        """Persist player, game, and clan state into the slot database."""
        conn = self._get_conn(slot)
        now = datetime.utcnow().isoformat()

        with conn:
            # Player state
            conn.execute(
                "INSERT OR REPLACE INTO player_state (id, data) VALUES (1, ?)",
                (json.dumps(player_data),),
            )
            # Game state
            conn.execute(
                "INSERT OR REPLACE INTO game_state (id, data) VALUES (1, ?)",
                (json.dumps(game_state_data),),
            )
            # Clan states
            for clan_id, data in clan_states.items():
                conn.execute(
                    "INSERT OR REPLACE INTO clan_states (clan_id, data) VALUES (?, ?)",
                    (clan_id, json.dumps(data)),
                )
            # Metadata
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("save_time", now),
            )
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("version", _SAVE_VERSION),
            )
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("auto_save", json.dumps(auto)),
            )

    def load_game(self, slot: str) -> dict | None:
        """Load player, game, and clan state. Returns *None* if no save."""
        db_path = self._db_path(slot)
        if not db_path.exists():
            return None

        conn = self._get_conn(slot)

        row = conn.execute("SELECT data FROM player_state WHERE id = 1").fetchone()
        if row is None:
            return None
        player_data = json.loads(row["data"])

        row = conn.execute("SELECT data FROM game_state WHERE id = 1").fetchone()
        game_state_data = json.loads(row["data"]) if row else {}

        clan_rows = conn.execute("SELECT clan_id, data FROM clan_states").fetchall()
        clan_states = {r["clan_id"]: json.loads(r["data"]) for r in clan_rows}

        return {
            "player_data": player_data,
            "game_state_data": game_state_data,
            "clan_states": clan_states,
        }

    # -- chunk persistence --------------------------------------------------

    def _chunk_path(
        self, slot: str, region_col: int, region_row: int, area_x: int, area_y: int
    ) -> Path:
        return (
            self._slot_dir(slot)
            / "chunks"
            / f"{region_col}_{region_row}"
            / f"{area_x}_{area_y}.dat"
        )

    def save_chunk(
        self,
        slot: str,
        region_col: int,
        region_row: int,
        area_x: int,
        area_y: int,
        chunk_data,
    ) -> None:
        """Compress and write *chunk_data* to a flat file."""
        path = self._chunk_path(slot, region_col, region_row, area_x, area_y)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(serialize_chunk(chunk_data))

    def load_chunk(
        self,
        slot: str,
        region_col: int,
        region_row: int,
        area_x: int,
        area_y: int,
    ):
        """Read and decompress chunk data, or return *None* if absent."""
        path = self._chunk_path(slot, region_col, region_row, area_x, area_y)
        if not path.exists():
            return None
        return deserialize_chunk(path.read_bytes())

    # -- explored areas -----------------------------------------------------

    def mark_explored(
        self,
        slot: str,
        region_col: int,
        region_row: int,
        area_x: int,
        area_y: int,
        modified: bool = False,
    ) -> None:
        """Record an area as explored (and optionally modified)."""
        conn = self._get_conn(slot)
        now = datetime.utcnow().isoformat()
        with conn:
            conn.execute(
                """INSERT OR REPLACE INTO explored_areas
                   (region_col, region_row, area_x, area_y, modified, explore_time)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (region_col, region_row, area_x, area_y, int(modified), now),
            )

    def is_explored(
        self,
        slot: str,
        region_col: int,
        region_row: int,
        area_x: int,
        area_y: int,
    ) -> bool:
        conn = self._get_conn(slot)
        row = conn.execute(
            """SELECT 1 FROM explored_areas
               WHERE region_col = ? AND region_row = ? AND area_x = ? AND area_y = ?""",
            (region_col, region_row, area_x, area_y),
        ).fetchone()
        return row is not None

    def is_modified(
        self,
        slot: str,
        region_col: int,
        region_row: int,
        area_x: int,
        area_y: int,
    ) -> bool:
        conn = self._get_conn(slot)
        row = conn.execute(
            """SELECT modified FROM explored_areas
               WHERE region_col = ? AND region_row = ? AND area_x = ? AND area_y = ?""",
            (region_col, region_row, area_x, area_y),
        ).fetchone()
        if row is None:
            return False
        return bool(row["modified"])

    # -- save management ----------------------------------------------------

    def list_saves(self) -> list[dict]:
        """Return a list of slot info dicts for every save on disk."""
        if not self.save_dir.exists():
            return []

        saves: list[dict] = []
        for entry in sorted(self.save_dir.iterdir()):
            db_path = entry / "save.db"
            if not entry.is_dir() or not db_path.exists():
                continue
            info: dict = {"slot": entry.name}
            try:
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                for row in conn.execute("SELECT key, value FROM metadata"):
                    info[row["key"]] = row["value"]
                conn.close()
            except sqlite3.Error:
                pass
            saves.append(info)
        return saves

    def delete_save(self, slot: str) -> None:
        """Remove a save directory and all its contents."""
        # Close any open connection first
        conn = self._connections.pop(slot, None)
        if conn is not None:
            conn.close()
        slot_dir = self._slot_dir(slot)
        if slot_dir.exists():
            shutil.rmtree(slot_dir)

    def auto_save(
        self,
        slot: str,
        player_data: dict,
        game_state_data: dict,
        clan_states: dict,
    ) -> None:
        """Same as save_game but marks the save as an auto-save."""
        self.save_game(slot, player_data, game_state_data, clan_states, auto=True)

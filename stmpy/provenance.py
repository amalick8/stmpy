"""Reproducible records for STMPY analysis runs.

The record is deliberately small and JSON-based so it can be saved beside a
figure or processed data file without requiring a database or notebook plugin.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Mapping, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _file_details(path: os.PathLike[str] | str) -> Dict[str, Any]:
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        raise FileNotFoundError(
            "Cannot add a provenance file that does not exist: '{}'".format(
                file_path
            )
        )

    digest = hashlib.sha256()
    with file_path.open("rb") as file_object:
        for block in iter(lambda: file_object.read(1024 * 1024), b""):
            digest.update(block)

    return {
        "path": str(file_path),
        "name": file_path.name,
        "size_bytes": file_path.stat().st_size,
        "sha256": digest.hexdigest(),
    }


def _json_value(value: Any) -> Any:
    """Convert common scientific Python values into JSON-compatible values."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, os.PathLike):
        return os.fspath(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]

    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            return _json_value(item_method())
        except ValueError:
            pass

    list_method = getattr(value, "tolist", None)
    if callable(list_method):
        return _json_value(list_method())

    raise TypeError(
        "Analysis parameters must be JSON-compatible; got {!r}.".format(
            type(value).__name__
        )
    )


def _data_summary(data: Any) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"type": type(data).__name__}
    arrays = {}
    for name in ("Z", "I", "LIY", "en", "didv"):
        value = getattr(data, name, None)
        shape = getattr(value, "shape", None)
        if shape is not None:
            arrays[name] = {
                "shape": list(shape),
                "dtype": str(getattr(value, "dtype", "unknown")),
            }
    if arrays:
        summary["arrays"] = arrays
    return summary


@dataclass
class AnalysisRecord:
    """Collect enough information to reproduce an analysis later.

    Parameters are optional and may contain normal Python values, paths, and
    NumPy scalars or arrays. Input and output files are fingerprinted with
    SHA-256 so a researcher can confirm which exact files were used.
    """

    name: str
    parameters: Mapping[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)
    inputs: List[Dict[str, Any]] = field(default_factory=list, init=False)
    outputs: List[Dict[str, Any]] = field(default_factory=list, init=False)
    steps: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("AnalysisRecord name must be a non-empty string.")
        self.name = self.name.strip()
        self.parameters = _json_value(dict(self.parameters))

    def add_input(self, path: os.PathLike[str] | str) -> Dict[str, Any]:
        details = _file_details(path)
        if not any(item["sha256"] == details["sha256"] for item in self.inputs):
            self.inputs.append(details)
        return details

    def add_output(self, path: os.PathLike[str] | str) -> Dict[str, Any]:
        details = _file_details(path)
        self.outputs.append(details)
        return details

    def add_step(
        self,
        name: str,
        parameters: Optional[Mapping[str, Any]] = None,
        result: Optional[Mapping[str, Any]] = None,
    ) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Analysis step name must be a non-empty string.")
        self.steps.append(
            {
                "name": name.strip(),
                "recorded_at": _utc_now(),
                "parameters": _json_value(dict(parameters or {})),
                "result": _json_value(dict(result or {})),
            }
        )

    def record_load(
        self,
        path: os.PathLike[str] | str,
        file_type: str,
        options: Mapping[str, Any],
        data: Any,
    ) -> None:
        details = self.add_input(path)
        self.add_step(
            "load",
            parameters={"file_type": file_type, **dict(options)},
            result={"input_sha256": details["sha256"], **_data_summary(data)},
        )

    def to_dict(self) -> Dict[str, Any]:
        from stmpy import __version__

        return {
            "schema_version": 1,
            "analysis_name": self.name,
            "created_at": self.created_at,
            "stmpy_version": __version__,
            "parameters": dict(self.parameters),
            "inputs": list(self.inputs),
            "steps": list(self.steps),
            "outputs": list(self.outputs),
        }

    def save(self, path: os.PathLike[str] | str) -> Path:
        """Write the record atomically, avoiding a half-written JSON file."""
        destination = Path(path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=destination.parent,
                prefix="." + destination.name + ".",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_file.write(payload)
                temporary_name = temporary_file.name
            os.replace(temporary_name, destination)
        finally:
            if temporary_name and os.path.exists(temporary_name):
                os.unlink(temporary_name)

        return destination

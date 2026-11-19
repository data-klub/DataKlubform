"""Checks that the package imports and that the config files match spec section 7."""

import importlib
import pkgutil
from pathlib import Path

import pytest
import yaml

import house_prices

ROOT = Path(__file__).resolve().parents[1]
MODULES = [m.name for m in pkgutil.walk_packages(house_prices.__path__, "house_prices.")]


def load_config(name: str) -> dict:
    """Read one YAML file from config/."""
    return yaml.safe_load((ROOT / "config" / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module: str) -> None:
    importlib.import_module(module)


def test_pipeline_config() -> None:
    config = load_config("pipeline.yaml")
    assert [source["name"] for source in config["sources"]] == ["olx", "otodom"]
    assert config["delisting_missed_full_crawls"] == 3


def test_teryt_stays_text() -> None:
    # An unquoted TERYT code becomes a YAML int, which loses leading zeros (Dolnośląskie is "02").
    assert load_config("pipeline.yaml")["analysis_scope"] == [{"teryt": "1465"}]


def test_docs_named_in_claude_md_exist() -> None:
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    for name in ("docs/spec.md", "docs/handoff.md"):
        assert name in text
        assert (ROOT / name).is_file(), f"CLAUDE.md points to {name}, which is missing"

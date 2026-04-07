from __future__ import annotations

import json
from datetime import timezone

import pytest


def test_module_has_main():
    from bluetag import codex_usage

    assert callable(codex_usage.main)


def test_build_rows_supports_primary_and_secondary_windows():
    from bluetag import codex_usage

    payload = {
        "usage": {
            "primary": {
                "used_percent": 25,
                "limit_window_seconds": 18000,
                "reset_at": 1_900_000_000,
            },
            "secondary": {
                "used_percent": 40,
                "limit_window_seconds": 604800,
                "reset_at": 1_900_100_000,
            },
        }
    }

    rows = codex_usage.build_rows(payload, timezone.utc)

    assert [row.label for row in rows] == ["5h limit", "weekly limit"]
    assert [round(row.left_percent) for row in rows] == [75, 60]
    assert all("resets" in row.resets_text for row in rows)


def test_normalize_base_url_adds_backend_api():
    from bluetag import codex_usage

    assert (
        codex_usage.normalize_base_url("https://chatgpt.com")
        == "https://chatgpt.com/backend-api"
    )


def test_render_usage_image_matches_small_screen_size():
    from bluetag import codex_usage

    rows = [
        codex_usage.UsageRow("5h limit", 80.0, "resets 12:00"),
        codex_usage.UsageRow("weekly limit", 55.0, "resets 18:30 on 9 Apr"),
    ]

    image = codex_usage.render_usage_image(rows)

    assert image.size == (250, 122)


def test_example_wrapper_exposes_main():
    example_globals: dict[str, object] = {}
    example_path = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "examples"
        / "push_codex_usage.py"
    )
    exec(example_path.read_text(encoding="utf-8"), example_globals)

    assert callable(example_globals["main"])


def test_load_local_usage_summary_aggregates_latest_session_totals(tmp_path):
    from bluetag import codex_usage

    day_dir = tmp_path / "sessions" / "2026" / "04" / "07"
    day_dir.mkdir(parents=True)

    first_session = day_dir / "session-a.jsonl"
    first_session.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": "2026-04-07T09:00:00Z",
                        "type": "event_msg",
                        "payload": {"type": "token_count", "info": None},
                    }
                ),
                json.dumps(
                    {
                        "timestamp": "2026-04-07T09:05:00Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 100,
                                    "cached_input_tokens": 25,
                                    "output_tokens": 5,
                                    "reasoning_output_tokens": 2,
                                    "total_tokens": 105,
                                }
                            },
                        },
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    second_session = day_dir / "session-b.jsonl"
    second_session.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": "2026-04-07T10:00:00Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 200,
                                    "cached_input_tokens": 100,
                                    "output_tokens": 10,
                                    "reasoning_output_tokens": 3,
                                    "total_tokens": 210,
                                }
                            },
                        },
                    }
                ),
                json.dumps(
                    {
                        "timestamp": "2026-04-07T10:30:00Z",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 240,
                                    "cached_input_tokens": 120,
                                    "output_tokens": 12,
                                    "reasoning_output_tokens": 4,
                                    "total_tokens": 252,
                                }
                            },
                        },
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    summary = codex_usage.load_local_usage_summary(
        sessions_root=tmp_path / "sessions",
        target_day=__import__("datetime").date(2026, 4, 7),
    )

    assert summary.session_count == 2
    assert summary.input_tokens == 340
    assert summary.cached_input_tokens == 145
    assert summary.output_tokens == 17
    assert summary.reasoning_output_tokens == 6
    assert summary.total_tokens == 357

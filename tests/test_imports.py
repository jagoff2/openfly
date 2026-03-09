from __future__ import annotations


def test_imports() -> None:
    import brain.mock_backend  # noqa: F401
    import body.mock_body  # noqa: F401
    import bridge.controller  # noqa: F401
    import runtime.closed_loop  # noqa: F401
    import vision.feature_extractor  # noqa: F401
    import vision.flyvis_fast_path  # noqa: F401

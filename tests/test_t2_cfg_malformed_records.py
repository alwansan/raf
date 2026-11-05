"""Regression tests for fail-closed malformed synthetic CIL input (no game assets)."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("t2_cfg", Path(__file__).resolve().parents[1] / "scripts" / "t2_rt_return_cfg.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_malformed_instruction_records_fail_closed():
    for program in ([None], [42], [()], [("ldnull", "unexpected", "extra")], [["ret", 1, 2]], [("ldnull",), None]):
        assert module.classify(program) == module.UNKNOWN


def test_malformed_bounds_fail_closed():
    for bounds in ({"max_states": True}, {"max_stack": 1.5}, {"max_locals": "10"}, {"max_states": 0}):
        assert module.classify([("ldnull",), ("ret",)], **bounds) == module.UNKNOWN


def test_valid_return_preserved():
    assert module.classify([("newobj_rt",), ("ret",)]) == module.CONSTRUCTED
    assert module.classify([("ldnull",), ("ret",)]) == module.NULL

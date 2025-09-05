from __future__ import annotations

from resobot_gw import __version__
from resobot_gw.__main__ import main


def test_version_flag_prints_version(capsys) -> None:
    code = main(["--version"])
    captured = capsys.readouterr()
    assert code == 0
    assert __version__ in captured.out


def test_help_when_no_args(capsys) -> None:
    code = main([])
    captured = capsys.readouterr()
    assert code == 2
    # argparse may print to stdout or stderr depending on environment
    both = captured.err + captured.out
    assert "usage:" in both

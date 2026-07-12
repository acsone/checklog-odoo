# SPDX-FileCopyrightText: 2023-present ACSONE <https://acsone.eu>
#
# SPDX-License-Identifier: MIT

import os

from click.testing import CliRunner

from checklog_odoo.checklog import checklog_odoo

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def test1():
    runner = CliRunner()
    res = runner.invoke(checklog_odoo, [os.path.join(DATA_DIR, "test1.log")])
    assert res.exit_code != 0
    expected = "errors that caused failure (2):"
    assert expected in res.output


def test2():
    runner = CliRunner()
    res = runner.invoke(checklog_odoo, ["--ignore", " ERROR ", os.path.join(DATA_DIR, "test1.log")])
    assert res.exit_code != 0
    expected = "errors that caused failure (1):"
    assert expected in res.output
    expected = "errors that did not cause failure (1):"
    assert expected in res.output


def test3():
    runner = CliRunner()
    res = runner.invoke(
        checklog_odoo,
        ["-i", " ERROR ", "-i", " CRITICAL ", os.path.join(DATA_DIR, "test1.log")],
    )
    assert res.exit_code == 0
    expected = "errors that did not cause failure (2):"
    assert expected in res.output


def test4():
    runner = CliRunner()
    res = runner.invoke(
        checklog_odoo,
        [
            "-c",
            os.path.join(DATA_DIR, "test_checklog.cfg"),
            os.path.join(DATA_DIR, "test1.log"),
        ],
    )
    assert res.exit_code != 0
    expected = "errors that caused failure (1):"
    assert expected in res.output
    expected = "errors that did not cause failure (1):"
    assert expected in res.output


def test_empty():
    runner = CliRunner()
    res = runner.invoke(checklog_odoo, [os.path.join(DATA_DIR, "empty.log")])
    assert res.exit_code != 0
    expected = "No Odoo log record found in input."
    assert expected in res.output
    res = runner.invoke(checklog_odoo, ["--no-err-if-empty", os.path.join(DATA_DIR, "empty.log")])
    assert res.exit_code == 0


def test_odoo_skipped_test_log():
    runner = CliRunner()
    res = runner.invoke(checklog_odoo, [os.path.join(DATA_DIR, "skipped_odoo.log")])
    assert res.exit_code != 0
    expected = "skipped tests detected (1):"
    assert expected in res.output
    expected = "Skipped tests detected in log."
    assert expected in res.output


def test_pytest_skipped_test_output():
    runner = CliRunner()
    res = runner.invoke(checklog_odoo, [os.path.join(DATA_DIR, "skipped_pytest.log")])
    assert res.exit_code != 0
    expected = "Skipped: Accounting Tests skipped because the user's company has no chart of accounts."
    assert expected in res.output


def test_pytest_skipped_progress_output():
    runner = CliRunner()
    for filename in ("skipped_pytest_progress.log", "skipped_pytest_verbose.log"):
        res = runner.invoke(checklog_odoo, [os.path.join(DATA_DIR, filename)])
        assert res.exit_code != 0
        expected = "SKIPPED odoo/addons/module/tests/test_model.py::TestModel::test_foo"
        assert expected in res.output


def test_no_err_on_skipped():
    runner = CliRunner()
    res = runner.invoke(checklog_odoo, ["--no-err-on-skipped", os.path.join(DATA_DIR, "skipped_odoo.log")])
    assert res.exit_code == 0
    expected = "skipped tests detected (1):"
    assert expected in res.output


def test_no_err_on_skipped_from_config():
    runner = CliRunner()
    res = runner.invoke(
        checklog_odoo,
        [
            "-c",
            os.path.join(DATA_DIR, "no_err_on_skipped.cfg"),
            os.path.join(DATA_DIR, "skipped_odoo.log"),
        ],
    )
    assert res.exit_code == 0
    expected = "skipped tests detected (1):"
    assert expected in res.output


def test_allowed_skipped_from_config():
    runner = CliRunner()
    res = runner.invoke(
        checklog_odoo,
        [
            "-c",
            os.path.join(DATA_DIR, "allowed_skipped.cfg"),
            os.path.join(DATA_DIR, "skipped_pytest_progress.log"),
        ],
    )
    assert res.exit_code == 0
    unexpected = "skipped tests detected"
    assert unexpected not in res.output


def test_unexpected_skipped_with_allowed_skipped_from_config():
    runner = CliRunner()
    res = runner.invoke(
        checklog_odoo,
        [
            "-c",
            os.path.join(DATA_DIR, "allowed_skipped.cfg"),
            os.path.join(DATA_DIR, "skipped_pytest_progress_mixed.log"),
        ],
    )
    assert res.exit_code != 0
    expected = "skipped tests detected (1):"
    assert expected in res.output
    expected = "SKIPPED odoo/addons/module/tests/test_model.py::TestModel::test_bar"
    assert expected in res.output


def test_skipped_false_positives():
    runner = CliRunner()
    res = runner.invoke(checklog_odoo, [os.path.join(DATA_DIR, "skipped_false_positive.log")])
    assert res.exit_code == 0
    unexpected = "skipped tests detected"
    assert unexpected not in res.output

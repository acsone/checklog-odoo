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

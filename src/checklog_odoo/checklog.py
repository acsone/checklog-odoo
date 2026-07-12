# SPDX-FileCopyrightText: 2023-present ACSONE <https://acsone.eu>
#
# SPDX-License-Identifier: MIT

import logging
import re
import sys

import click

from checklog_odoo.config import DEFAULT_CONFIG_FILE, ChecklogConfig

_logger = logging.getLogger(__name__)


# from tartley/colorama
ANSI_CSI_RE = re.compile("\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?")

# from OCA/maintainer-quality-tools
LOG_START_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \d+ (?P<loglevel>\w+) "
    r"(?P<db>\S+) (?P<logger>\S+): (?P<message>.*)$"
)

NON_ERROR_LEVELS = ("INFO", "DEBUG")
ODOO_TEST_SUITE_LOGGER = "odoo.tests.suite"
PYTEST_SKIPPED_PREFIX = "Skipped: "
PYTEST_SKIPPED_RE = re.compile(
    r"(?:^|\s)SKIPPED\s+(?P<nodeid_after>\S+\.py::\S+)|(?P<nodeid_before>\S+\.py::\S+)\s+SKIPPED(?:\s|\[|$)"
)


def _get_skipped_test_message(line, mo):
    if mo:
        if mo.group("logger") != ODOO_TEST_SUITE_LOGGER:
            return None
        message = mo.group("message")
        if message.startswith("skipped "):
            return message
        return None

    message = line.strip()
    if message.startswith(PYTEST_SKIPPED_PREFIX):
        return message
    skipped_match = PYTEST_SKIPPED_RE.search(message)
    if skipped_match:
        nodeid = skipped_match.group("nodeid_after") or skipped_match.group("nodeid_before")
        return f"SKIPPED {nodeid}"
    return None


def _render_errors(error_records, ignored_error_records):
    msg = []
    if ignored_error_records:
        msg.append(
            click.style(
                f"\nerrors that did not cause failure ({len(ignored_error_records)}):\n",
                bold=True,
            )
        )
        msg.extend(ignored_error_records)
    if error_records:
        msg.append(
            click.style(
                f"\nerrors that caused failure ({len(error_records)}):\n",
                bold=True,
            )
        )
        msg.extend(error_records)
    return "".join(msg)


def do_checklog(filename, ignore, echo, *, err_if_empty=True, err_on_skipped=True):
    ignore = [i for i in ignore if not i.startswith("#")]
    _logger.debug("ignored regular expressions:\n%s", "\n".join(ignore))
    ignore_regexes = [re.compile(i, re.MULTILINE) for i in ignore]

    if echo is None and filename == "-":
        echo = True

    with click.open_file(filename) as logfile:
        cur_rec_mo = None
        cur_rec = []
        error_records = []
        ignored_error_records = []
        skipped_test_messages = []
        skipped_test_message_set = set()

        def _process_cur_rec():
            # record start, process current record
            if cur_rec_mo and cur_rec_mo.group("loglevel") not in NON_ERROR_LEVELS:
                record = "".join(cur_rec)
                for ignore_regex in ignore_regexes:
                    if ignore_regex.search(record):
                        ignored_error_records.append(record)
                        break
                else:
                    error_records.append(record)

        reccount = 0
        for line in logfile:
            if echo:
                click.echo(line, nl=False, color=True)
                sys.stdout.flush()
            line_nocolor = ANSI_CSI_RE.sub("", line)  # strip ANSI colors
            mo = LOG_START_RE.match(line_nocolor)
            skipped_test_message = _get_skipped_test_message(line_nocolor, mo)
            if skipped_test_message and skipped_test_message not in skipped_test_message_set:
                skipped_test_message_set.add(skipped_test_message)
                if any(ignore_regex.search(skipped_test_message) for ignore_regex in ignore_regexes):
                    ignored_error_records.append(f"{skipped_test_message}\n")
                else:
                    skipped_test_messages.append(skipped_test_message)
            if mo:
                reccount += 1
                _process_cur_rec()
                cur_rec_mo = mo
                cur_rec = [line_nocolor]
            else:
                cur_rec.append(line_nocolor)
        _process_cur_rec()  # last record

        if not reccount and not skipped_test_message_set and err_if_empty:
            msg = "No Odoo log record found in input."
            raise click.ClickException(msg)

        if error_records or ignored_error_records:
            msg = _render_errors(error_records, ignored_error_records)
            click.echo(msg)
        if skipped_test_messages:
            click.echo(click.style(f"\nskipped tests detected ({len(skipped_test_messages)}):\n", bold=True))
            click.echo("\n".join(skipped_test_messages))
        if error_records:
            msg = "Errors detected in log."
            raise click.ClickException(msg)
        if skipped_test_messages and err_on_skipped:
            msg = "Skipped tests detected in log."
            raise click.ClickException(msg)


class ColoredFormatter(logging.Formatter):
    COLORS = {  # noqa: RUF012
        "DEBUG": {"dim": True},
        "INFO": {},
        "WARNING": {"fg": "yellow"},
        "ERROR": {"fg": "red"},
        "CRITICAL": {"fg": "white", "bg": "red"},
    }

    def format(self, record):
        res = super().format(record)
        return click.style(res, **self.COLORS[record.levelname])


@click.command(help="Check an odoo log file for errors. When no filename or - is provided, read from stdin.")
@click.option(
    "--ignore",
    "-i",
    metavar="REGEX",
    multiple=True,
    help="Regular expression of log records to ignore.",
)
@click.option(
    "--echo/--no-echo",
    default=None,
    help="Echo the input file (default when reading from stdin).",
)
@click.option(
    "--err-if-empty/--no-err-if-empty",
    default=True,
    help="Exit with an error code if no log record is found (default).",
)
@click.option(
    "--err-on-skipped/--no-err-on-skipped",
    default=None,
    help="Exit with an error code if skipped tests are found (default).",
)
@click.option("-v", "--verbose", count=True)
@click.option(
    "-c",
    "--config",
    type=click.Path(dir_okay=False, exists=True),
    help=f"Configuration file [default: {DEFAULT_CONFIG_FILE}].",
)
@click.argument("filename", type=click.Path(dir_okay=False), default="-")
@click.pass_context
def checklog_odoo(ctx, filename, config, ignore, verbose, echo, err_if_empty, err_on_skipped):
    config = ChecklogConfig(config)

    ctx.obj = {"config": config}

    ctx.default_map = config.get_default_map()

    checklog_config = ctx.default_map.get("checklog")
    default_ignore = checklog_config.get("ignore")
    if not ignore and default_ignore:
        ignore = default_ignore
    default_err_on_skipped = checklog_config.get("err_on_skipped")
    if err_on_skipped is None:
        err_on_skipped = True if default_err_on_skipped is None else default_err_on_skipped

    if verbose > 1:
        level = logging.DEBUG
    elif verbose > 0:
        level = logging.INFO
    else:
        level = logging.WARNING

    logger = logging.getLogger()
    channel = logging.StreamHandler()
    channel.setFormatter(ColoredFormatter())
    logger.setLevel(level)
    logger.addHandler(channel)

    do_checklog(
        filename,
        ignore,
        echo,
        err_if_empty=err_if_empty,
        err_on_skipped=err_on_skipped,
    )


def _read_defaults(config):
    section = "checklog-odoo"
    defaults = {
        "ignore": config.getlist(section, "ignore", []),
        "echo": config.getboolean(section, "echo", None),
        "err_on_skipped": config.getboolean(section, "err_on_skipped", None),
    }
    return {"checklog": defaults}


ChecklogConfig.add_default_map_reader(_read_defaults)

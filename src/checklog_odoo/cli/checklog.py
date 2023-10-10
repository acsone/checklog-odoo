# SPDX-FileCopyrightText: 2023-present Benoit Aimont <benoit.aimont@acsone.eu>
#
# SPDX-License-Identifier: MIT

from checklog_odoo.__about__ import __version__

import logging
import re
import sys

import click

from checklog_odoo.config import ChecklogConfig

_logger = logging.getLogger(__name__)


# from tartley/colorama
ANSI_CSI_RE = re.compile("\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?")

# from OCA/maintainer-quality-tools
LOG_START_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \d+ (?P<loglevel>\w+) "
    r"(?P<db>\S+) (?P<logger>\S+): (?P<message>.*)$"
)

NON_ERROR_LEVELS = ("INFO", "DEBUG")


def _render_errors(error_records, ignored_error_records):
    msg = []
    if ignored_error_records:
        msg.append(
            click.style(
                "\nerrors that did not cause failure ({}):\n".format(
                    len(ignored_error_records)
                ),
                bold=True,
            )
        )
        msg.extend(ignored_error_records)
    if error_records:
        msg.append(
            click.style(
                "\nerrors that caused failure ({}):\n".format(len(error_records)),
                bold=True,
            )
        )
        msg.extend(error_records)
    return "".join(msg)


def do_checklog(filename, ignore, echo, err_if_empty=True):
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
            line = ANSI_CSI_RE.sub("", line)  # strip ANSI colors
            mo = LOG_START_RE.match(line)
            if mo:
                reccount += 1
                _process_cur_rec()
                cur_rec_mo = mo
                cur_rec = [line]
            else:
                cur_rec.append(line)
        _process_cur_rec()  # last record

        if not reccount and err_if_empty:
            raise click.ClickException("No Odoo log record found in input.")

        if error_records or ignored_error_records:
            msg = _render_errors(error_records, ignored_error_records)
            click.echo(msg)
        if error_records:
            raise click.ClickException("Errors detected in log.")

class ColoredFormatter(logging.Formatter):

    COLORS = {
        "DEBUG": dict(dim=True),
        "INFO": dict(),
        "WARNING": dict(fg="yellow"),
        "ERROR": dict(fg="red"),
        "CRITICAL": dict(fg="white", bg="red"),
    }

    def format(self, record):
        res = super(ColoredFormatter, self).format(record)
        return click.style(res, **self.COLORS[record.levelname])

@click.command(
    help="Check an odoo log file for errors. When no filename "
    "or - is provided, read from stdin."
)
@click.version_option(version=__version__, prog_name="checklog-odoo")
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
    help="Exit with an error code if no log record is found " "(default).",
)
@click.option("-v", "--verbose", count=True)
@click.option(
    "-c",
    "--config",
    type=click.Path(dir_okay=False, exists=True),
    help="Configuration file (default: ./checklog.cfg).",
)
@click.argument("filename", type=click.Path(dir_okay=False), default="-")
@click.pass_context
def checklog_odoo(ctx, filename, config, ignore, verbose, echo, err_if_empty):
    config = ChecklogConfig(config)

    ctx.obj = dict(config=config)

    ctx.default_map = config.get_default_map()

    checklog_config = ctx.default_map.get('checklog')
    default_ignore = checklog_config.get('ignore')
    if not ignore and default_ignore:
        ignore = default_ignore

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

    do_checklog(filename, ignore, echo, err_if_empty)


def _read_defaults(config):
    section = "checklog"
    defaults = dict(
        ignore=config.getlist(section, "ignore", []),
        echo=config.getboolean(section, "echo", None),
    )
    return dict(checklog=defaults)

ChecklogConfig.add_default_map_reader(_read_defaults)
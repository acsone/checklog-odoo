# SPDX-FileCopyrightText: 2023-present ACSONE <https://acsone.eu>
#
# SPDX-License-Identifier: MIT

import os
from configparser import NoOptionError, NoSectionError, RawConfigParser
from pathlib import Path

import click

from .compat import tomllib

DEFAULT_CONFIG_FILE = "checklog-odoo.cfg"
SECTION = "checklog"


def _split_multiline(s):
    return [i.strip() for i in s.splitlines() if i.strip()]


class ChecklogConfig:
    # list of callables returning dictionaries to update default_map
    default_map_readers = []  # noqa: RUF012

    def __init__(self, filename):
        self.__cfg = RawConfigParser()
        if not filename and os.path.isfile(DEFAULT_CONFIG_FILE):
            filename = DEFAULT_CONFIG_FILE
        if filename:
            if not os.path.isfile(filename):
                msg = f"Configuration file {filename} not found."
                raise click.ClickException(msg)
            self.__cfgfile = filename
            self.__cfg.read(filename)
        pyproject_path = Path("pyproject.toml")
        self.__pyproject = {}
        if pyproject_path.is_file():
            self.__pyproject = tomllib.loads(pyproject_path.read_text())

    @staticmethod
    def add_default_map_reader(reader):
        ChecklogConfig.default_map_readers.append(reader)

    def get_default_map(self):
        default_map = {}
        for reader in self.default_map_readers:
            default_map.update(reader(self))
        return default_map

    def get(self, section, option, default=None, *, flatten=False):
        try:
            r = self.__cfg.get(section, option)
            if flatten:
                r = "".join(_split_multiline(r))
            return r
        except (NoOptionError, NoSectionError):
            return default

    def getboolean(self, section, option, default=None):
        try:
            return self.__cfg.getboolean(section, option)
        except (NoOptionError, NoSectionError):
            return default

    def getlist(self, section, option, default=None):
        try:
            return _split_multiline(self.__cfg.get(section, option))
        except (NoOptionError, NoSectionError):
            return default or []

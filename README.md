# checklog-odoo

[![PyPI - Version](https://img.shields.io/pypi/v/checklog-odoo.svg)](https://pypi.org/project/checklog-odoo)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/checklog-odoo.svg)](https://pypi.org/project/checklog-odoo)

-----

<!--- shortdesc-begin -->

Check if an odoo log file contains error, with the possibility to ignore some errors based on regular expressions.

This project replaces the [acsoo](https://pypi.org/project/acsoo)'s checklog command.

<!--- shortdesc-end -->

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pipx install checklog-odoo
```

## Use examples

```console
checklog-odoo odoo.log
unbuffer odoo -d mydb -i base --stop-after-init | checklog-odoo
checklog-odoo --ignore "WARNING.*blah" odoo.log
```

## Usage

```console
Usage: checklog-odoo [OPTIONS] [FILENAME]

  Check an odoo log file for errors. When no filename or - is provided, read
  from stdin.

Options:
  -i, --ignore REGEX              Regular expression of log records to ignore.
  --echo / --no-echo              Echo the input file (default when reading
                                  from stdin).
  --err-if-empty / --no-err-if-empty
                                  Exit with an error code if no log record is
                                  found (default).
  -v, --verbose
  -c, --config FILE               Configuration file  [default: checklog-odoo.cfg]
  --help                          Show this message and exit.
```

## Example of config file:

The configuration file use the `ini` format:

```ini
[checklog-odoo]
ignore=
   WARNING
   ERROR:.*registry
```

## License

`checklog-odoo` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

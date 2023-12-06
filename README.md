# checklog-odoo

[![PyPI - Version](https://img.shields.io/pypi/v/checklog-odoo.svg)](https://pypi.org/project/checklog-odoo)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/checklog-odoo.svg)](https://pypi.org/project/checklog-odoo)

-----

<!--- shortdesc-begin -->

Check if an odoo log file contains error, with the possibility to ignore some errors based on regular expressions.
Replaces acsoo checklog (https://github.com/acsone/acsoo#id5).

<!--- shortdesc-end -->

**Table of Contents**

- [Installation](#installation)
- [Features](#features)
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

## Options

* -i, --ignore REGEX:              Regular expression of log records to ignore.
* --echo / --no-echo:              Echo the input file (default when reading
                                  from stdin).
* --err-if-empty / --no-err-if-empty:
                                  Exit with an error code if no log record is
                                  found (default).
*  -c, --config FILE:               Configuration file (default:
                                  ./checklog.cfg).
   * Example of config file:
        ```console
        [checklog]
        ignore=
           WARNING
           ERROR:.*registry
        ```


*  --help:                          Show the help message and exit.


## License

`checklog-odoo` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

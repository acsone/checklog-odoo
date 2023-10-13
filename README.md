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
pip install checklog-odoo
```

## Features

```console
checklog-odoo odoo.log
unbuffer odoo -d mydb -i base --stop-after-init | checklog-odoo
checklog-odoo --ignore "WARNING.*blah" odoo.log
```

## License

`checklog-odoo` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

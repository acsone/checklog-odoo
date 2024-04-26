# SPDX-FileCopyrightText: 2023-present ACSONE <https://acsone.eu>
#
# SPDX-License-Identifier: MIT
import sys

if __name__ == "__main__":
    from checklog_odoo.checklog import checklog_odoo

    sys.exit(checklog_odoo())

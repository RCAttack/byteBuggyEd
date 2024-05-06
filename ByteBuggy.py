#!/usr/bin/env python

# Note: This script runs ByteBuggy from within a cloned git repo.
# The script `bin/ByteBuggy` is designed to be run after installing (from /usr/sbin), not from the cwd.

from byteBuggy import __main__
__main__.entry_point()

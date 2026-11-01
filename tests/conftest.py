"""Project-wide pytest setup."""

import os

# Qt must never open real windows during tests. This has to be set before
# any Qt module creates a QApplication.
os.environ["QT_QPA_PLATFORM"] = "offscreen"

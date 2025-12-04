# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

"""
Module for common constants and utils.
"""

import logging
from collections import namedtuple

TidyFindings = namedtuple("TidyFindings", "errors warnings suppressions nolints counting")

# Controls whether to use a custom warning filter or use the clang-tidy output
SHALL_USE_FILTER = True

# INFO is the assumed production log level
SILENT_LOG_LEVEL = logging.WARNING
DEFAULT_LOG_LEVEL = logging.INFO
VERBOSE_LOG_LEVEL = logging.DEBUG

NO_FIXES_REQUIRED = "No fix(es) required or possible\n"


class ConfigException(Exception):
    """A config exception class used for validating config merges."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

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
This module contains logic for clang-tidy checks for tidy_suite aspect
"""

# All supported checks when using the 'checks' parameter
AVAILABLE_CHECKS = [
    "bugprone-*",
    "cert-*",
    "clang-analyzer-*",
    "concurrency-*",
    "cppcoreguidelines-*",
    "google-*",
    "hicpp-*",
    "llvm-*",
    "llvmlibc-*",
    "misc-*",
    "modernize-*",
    "performance-*",
    "portability-*",
    "readability-*",
]

def _tidy_suite_generate_checks_strings():
    """Generate naive permutations of available checks"""
    values = [".clang-tidy", "*", "-*"]
    available_checks = AVAILABLE_CHECKS

    for check in available_checks:
        values.append(check)
        values.append("-" + check)
        values.append("*," + "-" + check)
    return values

# Holds all naively combined check options
AVAILABLE_CHECKS_COMBINED = _tidy_suite_generate_checks_strings()

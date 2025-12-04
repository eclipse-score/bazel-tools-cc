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

"""This module defines the offered providers of the Clang-format aspect."""

ClangFormatConfigInfo = provider(
    doc = "Configuration structure for the Clang-format aspect",
    fields = {
        "config_file": "File label pointing to a user-supplied .clang-format config file.",
        "exclude_types": "List of target types that the Clang-format aspect should not consider.",
        "excludes": "List of sources to be excluded from the Clang-format analysis.",
        "excludes_override": "List of excluded sources w.r.t. `excludes` to be included in Clang-format analysis nonetheless.",
        "target_types": "List of target types that the Clang-format aspect should consider, i.e. `cc_library`. If not provided, it will run on all targets which implement the CCInfo Provider.",
    },
)

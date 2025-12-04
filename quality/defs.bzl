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
Defines all public symbols for this modules to be used by the specific project.
"""

load(
    "@score_bazel_tools_cc//quality/private/clang_format:clang_format_aspect.bzl",
    _clang_format_aspect = "clang_format_aspect",
)
load(
    "@score_bazel_tools_cc//quality/private/clang_format:clang_format_config.bzl",
    _clang_format_config = "clang_format_config",
)
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_config.bzl",
    _quality_clang_tidy_config = "quality_clang_tidy_config",
    _quality_clang_tidy_forced_includes_config = "quality_clang_tidy_forced_includes_config",
    _quality_clang_tidy_include_files_config = "quality_clang_tidy_include_files_config",
    _quality_clang_tidy_priority_includes_config = "quality_clang_tidy_priority_includes_config",
)
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_runner.bzl",
    _quality_clang_tidy_aspect = "quality_clang_tidy_aspect",
)

clang_format_aspect = _clang_format_aspect
clang_format_config = _clang_format_config

# The actual aspect. Use this in your .bazelrc as such `--aspects=@score_bazel_tools_cc//quality:defs.bzl%quality_clang_tidy_aspect`
quality_clang_tidy_aspect = _quality_clang_tidy_aspect

# The clang-tidy aspect config. Add an instance of this config to one of your BUILD files as such `quality_clang_tidy_config(...)`
quality_clang_tidy_config = _quality_clang_tidy_config

# An optional additional config entry. Use an instance of this in your previously defined clang-tidy aspect config as such `quality_clang_tidy_config(clang_tidy_forced_includes=quality_clang_tidy_forced_includes_config(...))`
quality_clang_tidy_forced_includes_config = _quality_clang_tidy_forced_includes_config

# An optional additional config entry. Use an instance of this in your previously defined clang-tidy aspect config as such `quality_clang_tidy_config(clang_tidy_priority_includes=quality_clang_tidy_priority_includes_config(...))`
quality_clang_tidy_priority_includes_config = _quality_clang_tidy_priority_includes_config

# An additional config required by `quality_clang_tidy_priority_includes_config` (if used)
quality_clang_tidy_include_files_config = _quality_clang_tidy_include_files_config

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
Implementation of the tidy runner.
"""

load("@rules_python//python:defs.bzl", "py_binary")
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_aspect.bzl",
    "quality_clang_tidy_aspect_factory",
)

def clang_tidy_runner(name = None, data = None):
    """Macro redirection of tidy_runner to be imported from projects.

    Args:
        name: Target name of the tidy_tidy used by the aspect.
        data: Meant to have a dependency to a filegroup containing the .clang-tidy file.
    """
    py_binary(
        name = name,
        srcs = ["@score_bazel_tools_cc//quality/private/clang_tidy/tools:clang_tidy_runner.py"],
        main = "@score_bazel_tools_cc//quality/private/clang_tidy/tools:clang_tidy_runner.py",
        data = data,
        visibility = ["//visibility:public"],
        deps = ["@score_bazel_tools_cc//quality/private/clang_tidy/tools:clang_tidy_runner_lib"],
    )

quality_clang_tidy_aspect = quality_clang_tidy_aspect_factory(
    tidy_config = "@score_bazel_tools_cc//quality:quality_clang_tidy_config",
    tidy_runner = "@score_bazel_tools_cc//quality/private/clang_tidy:score_clang_tidy_tidy_runner",
)

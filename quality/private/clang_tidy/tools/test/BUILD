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

load("@bazel_tools_python//quality:defs.bzl", "py_pytest")

py_pytest(
    name = "test_clang_tidy_runner",
    srcs = ["test_clang_tidy_runner.py"],
    data = ["@score_bazel_tools_cc//quality/private/clang_tidy/tools/config:clang_tidy_config"],
    deps = ["@score_bazel_tools_cc//quality/private/clang_tidy/tools:clang_tidy_runner_lib"],
)

py_pytest(
    name = "test_clang_tidy_result_filter",
    srcs = ["test_clang_tidy_result_filter.py"],
    data = ["@score_bazel_tools_cc//quality/private/clang_tidy/tools/config:clang_tidy_config"],
    deps = ["@score_bazel_tools_cc//quality/private/clang_tidy/tools:clang_tidy_runner_lib"],
)

py_pytest(
    name = "test_clang_tidy_configs",
    srcs = ["test_clang_tidy_configs.py"],
    deps = ["@score_bazel_tools_cc//quality/private/clang_tidy/tools:clang_tidy_runner_lib"],
)

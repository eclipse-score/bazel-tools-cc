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
    name = "test_clang_format_runner",
    srcs = ["test_clang_format_runner.py"],
    deps = ["//quality/private/clang_format/tool:clang_format"],
)

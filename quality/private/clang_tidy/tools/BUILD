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

load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("@score_bazel_tools_cc_pip_hub//:loaders.bzl", "pkg")

py_library(
    name = "clang_tidy_runner_lib",
    srcs = glob(["*.py"]),
    data = ["@score_bazel_tools_cc//quality/private/clang_tidy/tools/config:clang_tidy_config"],
    visibility = ["//visibility:public"],
    deps = [
        pkg("ruamel.yaml"),
        pkg("termcolor"),
        "//quality/private/common/tools:utils",
        "@rules_python//python/runfiles",
    ],
)

# Wraps the toolchain clang-tidy binary via a python wrapper
py_binary(
    name = "clang_tidy_runner",
    srcs = ["clang_tidy_runner.py"],
    data = [
        "@score_bazel_tools_cc//quality/private/clang_tidy/tools/config:clang_tidy_config",
    ],
    visibility = ["//visibility:public"],
    deps = [":clang_tidy_runner_lib"],
)

# Required to instantiate the clang-tidy aspect from other projects
exports_files(["clang_tidy_runner.py"])

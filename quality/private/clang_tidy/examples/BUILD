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

load("@rules_cc//cc:defs.bzl", "cc_library")
load(
    "@score_bazel_tools_cc//quality/private/clang_tidy:tidy_suite.bzl",
    "tidy_suite",
)

# The main tidy_suite invoking multiple targets.
tidy_suite(
    name = "example_tidy",
    deps = [
        ":example1",
        ":example2",
    ],
)

# Test sources, same for all rules
SRCS = glob([
    "*.cpp",
    "*.h",
])

# A set of example libraries, one per instantiated tidy_suite rule.
# This is required, as the file name would be the same for tidy_suite.
# That means, only one tidy_suite rule is allowed per cc_library.
cc_library(
    name = "example1",
    srcs = SRCS,
    features = [
        "-treat_clang_tidy_warnings_as_errors",
    ],
)

cc_library(
    name = "example2",
    srcs = SRCS,
    features = [
        "-treat_clang_tidy_warnings_as_errors",
    ],
)

# A set of example libraries and tidy_suite targets to demonstrate advanced parameters.
cc_library(
    name = "example_one_rule",
    srcs = SRCS,
    features = [
        "-treat_clang_tidy_warnings_as_errors",
    ],
)

cc_library(
    name = "example_all_rules",
    srcs = SRCS,
)

tidy_suite(
    name = "example_tidy_one_rule",
    checks = [
        "bugprone-*",
    ],
    deps = [":example_one_rule"],
)

tidy_suite(
    name = "example_tidy_all_rules",
    checks = [
        "*",
        "-modernize-*",
    ],
    summary = True,
    deps = [":example_all_rules"],
)

cc_library(
    name = "example_clang_analyzer_checkers",
    srcs = SRCS,
    features = [
        "allow_analyzer_alpha_checkers_clang_tidy",
    ],
)

tidy_suite(
    name = "example_tidy_clang_analyzer_checkers",
    checks = ["clang-analyzer-*"],
    deps = [":example_clang_analyzer_checkers"],
)

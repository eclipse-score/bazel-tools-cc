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

load(
    "@score_bazel_tools_cc//quality:defs.bzl",
    "quality_clang_tidy_forced_includes_config",
)

filegroup(
    name = "forced_c_includes",
    srcs = [
        "forced_include_functions.h",
    ],
)

filegroup(
    name = "forced_cpp_includes",
    srcs = [
        "forced_include_functions.hpp",
    ],
)

quality_clang_tidy_forced_includes_config(
    name = "forced_includes",
    c_compile = [":forced_c_includes"],
    cpp_compile = [":forced_cpp_includes"],
    visibility = ["//quality/private/clang_tidy/test:__subpackages__"],
)

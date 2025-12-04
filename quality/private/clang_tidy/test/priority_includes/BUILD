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
    "quality_clang_tidy_include_files_config",
    "quality_clang_tidy_priority_includes_config",
)

filegroup(
    name = "all_headers",
    srcs = [
        "header_file_with_one_finding.h",
        "header_file_with_one_finding.hpp",
    ],
)

quality_clang_tidy_include_files_config(
    name = "priority_c_headers",
    include_prefix = "include",
    select_files = [
        "header_file_with_one_finding.h",
    ],
    source_files = [":all_headers"],
)

quality_clang_tidy_include_files_config(
    name = "priority_cpp_headers",
    include_prefix = "include",
    select_files = [
        "header_file_with_one_finding.hpp",
    ],
    source_files = [":all_headers"],
)

quality_clang_tidy_priority_includes_config(
    name = "priority_includes",
    c_compile = [":priority_c_headers"],
    cpp_compile = [":priority_cpp_headers"],
    visibility = ["//quality/private/clang_tidy/test:__subpackages__"],
)

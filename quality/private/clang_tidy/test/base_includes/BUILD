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

cc_library(
    name = "c_headers",
    hdrs = ["header_file_with_one_finding.h"],
    include_prefix = "include",
    strip_include_prefix = ".",
    visibility = ["//quality/private/clang_tidy/test:__subpackages__"],
)

cc_library(
    name = "cpp_headers",
    hdrs = ["header_file_with_one_finding.hpp"],
    include_prefix = "include",
    strip_include_prefix = ".",
    visibility = ["//quality/private/clang_tidy/test:__subpackages__"],
)

cc_library(
    name = "cpp_system_headers",
    hdrs = ["header_file_with_one_finding.hpp"],
    includes = ["."],
    visibility = ["//quality/private/clang_tidy/test:__subpackages__"],
)

exports_files(
    ["header_file_with_one_finding.hpp"],
    visibility = ["//quality/private/clang_tidy/test:__subpackages__"],
)

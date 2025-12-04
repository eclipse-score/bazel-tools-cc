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

load("@rules_shell//shell:sh_binary.bzl", "sh_binary")
load("@score_bazel_tools_cc//quality/private/clang_tidy/support:tidy_binary.bzl", "clang_tidy_binary")
load("@score_bazel_tools_cc//quality/private/clang_tidy/support:tidy_files.bzl", "clang_tidy_files")

exports_files(["clang_tidy_wrapper.tpl"])

clang_tidy_binary(
    name = "clang_tidy_binary",
    visibility = ["//visibility:public"],
)

clang_tidy_files(
    name = "clang_tidy_files",
    visibility = ["//visibility:public"],
)

sh_binary(
    name = "clang_tidy_local",
    srcs = ["clang_tidy_local.sh"],
    visibility = ["//visibility:public"],
)

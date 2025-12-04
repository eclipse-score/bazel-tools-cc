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
This module is able to determine the clang-tidy files from a exisiting clang toolchain.
"""

load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")

def _clang_tidy_files_impl(ctx):
    cc_toolchain = find_cpp_toolchain(ctx)

    return [
        DefaultInfo(
            files = cc_toolchain.all_files,
        ),
    ]

clang_tidy_files = rule(
    implementation = _clang_tidy_files_impl,
    fragments = ["cpp"],
    attrs = {
        "_cc_toolchain": attr.label(default = Label("@bazel_tools//tools/cpp:current_cc_toolchain")),
    },
    incompatible_use_toolchain_transition = True,
    toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
)

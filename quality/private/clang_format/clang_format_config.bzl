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

"""This module is the clang-format aspect configuration provider."""

load("@score_bazel_tools_cc//quality/private/clang_format:clang_format_providers.bzl", "ClangFormatConfigInfo")

def _clang_format_config_impl(ctx):
    return [
        ClangFormatConfigInfo(
            excludes = ctx.attr.excludes,
            excludes_override = ctx.attr.excludes_override,
            exclude_types = ctx.attr.exclude_types,
            target_types = ctx.attr.target_types,
            config_file = ctx.file.config_file,
        ),
    ]

clang_format_config = rule(
    implementation = _clang_format_config_impl,
    attrs = {
        "config_file": attr.label(
            allow_single_file = True,
            default = None,
            doc = "Optional user-supplied .clang-format config file.",
        ),
        "exclude_types": attr.string_list(
            default = [],
            allow_empty = True,
            doc = "List of target types that the Clang-format aspect should not consider.",
        ),
        "excludes": attr.string_list(
            default = [],
            mandatory = False,
            doc = "List of sources to be excluded from the Clang-format analysis.",
        ),
        "excludes_override": attr.string_list(
            default = [],
            mandatory = False,
            doc = "List of excluded sources w.r.t. `excludes` to be included in Clang-format analysis nonetheless.",
        ),
        "target_types": attr.string_list(
            default = ["<NONE>"],
            allow_empty = True,
            doc = (
                "List of target types that the Clang-format aspect should consider." +
                " Defaults to all targets which implements the CcInfo Provider."
            ),
        ),
    },
)

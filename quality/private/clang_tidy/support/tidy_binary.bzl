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
This module is able to determine the clang-tidy binary from a exisiting clang toolchain.
"""

load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "ACTION_NAMES")
load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")

def _clang_tidy_binary_impl(ctx):
    cc_toolchain = find_cpp_toolchain(ctx)

    feature_configuration = cc_common.configure_features(
        ctx = ctx,
        cc_toolchain = cc_toolchain,
        requested_features = ctx.features,
        unsupported_features = ctx.disabled_features,
    )

    clang_compiler_path = cc_common.get_tool_for_action(
        feature_configuration = feature_configuration,
        action_name = ACTION_NAMES.cpp_compile,
    )

    # Get the binary from the toolchain.
    # As long as there is no clear name how the "clang-tidy" action is called,
    # we simple take the compiler action which is alwayy available and expect
    # that the clang-tidy binary lives next to the compiler binary.
    clang_tidy_path = "/".join(clang_compiler_path.split("/")[:-1] + ["clang-tidy"])

    executable = ctx.actions.declare_file(ctx.attr.name)

    runfiles = ctx.runfiles(files = ctx.files.data)

    all_targets = ctx.attr.data
    runfiles = runfiles.merge_all([
        target[DefaultInfo].default_runfiles
        for target in all_targets
    ])

    ctx.actions.expand_template(
        template = ctx.file._wrapper_template,
        output = executable,
        substitutions = {
            "{clang_tidy_binary}": repr(clang_tidy_path),
        },
    )

    return [
        DefaultInfo(
            executable = executable,
            runfiles = runfiles,
            files = cc_toolchain.all_files,
        ),
    ]

clang_tidy_binary = rule(
    implementation = _clang_tidy_binary_impl,
    fragments = ["cpp"],
    attrs = {
        "data": attr.label_list(
            allow_files = True,
        ),
        "_cc_toolchain": attr.label(default = Label("@bazel_tools//tools/cpp:current_cc_toolchain")),
        "_wrapper_template": attr.label(
            allow_single_file = True,
            default = "clang_tidy_wrapper.tpl",
        ),
    },
    incompatible_use_toolchain_transition = True,
    toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
)

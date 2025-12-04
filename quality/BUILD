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

load("@score_bazel_tools_cc//quality:defs.bzl", "clang_format_config", "quality_clang_tidy_config")

quality_clang_tidy_config(
    name = "quality_clang_tidy_config_default",
    additional_flags = [],
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "default",
    dependency_attributes = [
        "deps",
    ],
    excludes = [],
    feature_mapping = {
        "@score_bazel_tools_cc//quality/private/clang_tidy/tools/config:.clang-tidy-default": "default",
    },
    target_types = [
        "cc_binary",
        "cc_library",
        "cc_test",
    ],
    unsupported_flags = [],
    visibility = ["//visibility:public"],
)

label_flag(
    name = "quality_clang_tidy_config",
    build_setting_default = "@score_bazel_tools_cc//quality:quality_clang_tidy_config_default",
    visibility = ["//visibility:public"],
)

alias(
    name = "clang_tidy_local",
    actual = "@score_bazel_tools_cc//quality/private/clang_tidy/support:clang_tidy_local",
    visibility = ["//visibility:public"],
)

clang_format_config(
    name = "clang_format_config_default",
    excludes = ["external/"],
    target_types = [
        "cc_binary",
        "cc_library",
        "cc_test",
    ],
    visibility = ["//visibility:public"],
)

label_flag(
    name = "clang_format_config",
    build_setting_default = "@score_bazel_tools_cc//quality:clang_format_config_default",
    visibility = ["//visibility:public"],
)

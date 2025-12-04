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

load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_cc//cc:cc_test.bzl", "cc_test")
load("@rules_shell//shell:sh_binary.bzl", "sh_binary")
load("@score_bazel_tools_cc//quality:defs.bzl", "clang_format_config", "quality_clang_tidy_config")

#####################
# C/CPP test targets.
#####################

cc_binary(
    name = "test_bin",
    srcs = ["test.cpp"],
)

cc_library(
    name = "test_lib_c",
    srcs = ["test.c"],
    hdrs = ["test.h"],
)

cc_library(
    name = "test_lib",
    srcs = ["test.cpp"],
    hdrs = ["test.h"],
)

cc_test(
    name = "test_test",
    srcs = ["test.cpp"],
    deps = [":test_lib"],
)

cc_library(
    name = "clean",
    srcs = ["clean.cpp"],
)

#####################
# Config clang-tidy.
#####################

filegroup(
    name = "clang_tidy_config",
    srcs = [
        ".clang-tidy",
        "awesome_config.yaml",
    ],
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "awesome_clang_tidy_config",
    additional_flags = [],
    clang_tidy_binary = "@llvm_toolchain//:clang-tidy",
    default_feature = "awesome",
    dependency_attributes = [
        "deps",
        "srcs",
    ],
    excludes = [],
    feature_mapping = {
        "//:.clang-tidy": "strict",
        "//:awesome_config.yaml": "awesome",
    },
    feature_mapping_c = {
        "//:awesome_config_c.yaml": "awesome",
    },
    target_types = [
        "cc_library",
    ],
    unsupported_flags = [],
    visibility = ["//visibility:public"],
)

sh_binary(
    name = "win_clang_tidy",
    srcs = ["win_clang_tidy.sh"],
    visibility = ["//visibility:public"],
)

quality_clang_tidy_config(
    name = "win_clang_tidy_config",
    additional_flags = [],
    clang_tidy_binary = ":win_clang_tidy",
    default_feature = "awesome",
    feature_mapping = {
        "//:.clang-tidy": "strict",
        "//:awesome_config.yaml": "awesome",
    },
    visibility = ["//visibility:public"],
)

######################
# Config clang-format.
######################

clang_format_config(
    name = "awesome_clang_format_config",
    config_file = "//:.clang_format",
    excludes = ["external/"],
    target_types = [
        "cc_binary",
        "cc_library",
        "cc_test",
    ],
    visibility = ["//visibility:public"],
)

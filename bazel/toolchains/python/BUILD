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

load("@bazel_skylib//rules:common_settings.bzl", "bool_flag", "bool_setting")
load("@rules_python//python:defs.bzl", "py_runtime_pair")
load("@score_bazel_tools_cc//bazel/toolchains/python:versions.bzl", "PYTHON_VERSIONS", "unsupported_python_configuration_error")

bool_flag(
    name = "internal_toolchains",
    build_setting_default = False,
)

config_setting(
    name = "use_internal_toolchains",
    flag_values = {":internal_toolchains": "True"},
)

config_setting(
    name = "do_not_use_internal_toolchains",
    flag_values = {":internal_toolchains": "False"},
)

config_setting(
    name = "python_undefined",
    flag_values = {"@rules_python//python/config_settings:python_version": ""},
    visibility = ["//visibility:public"],
)

[
    config_setting(
        name = "python_{}".format(version.replace(".", "_")),
        flag_values = {"@rules_python//python/config_settings:python_version_major_minor": version},
        visibility = ["//visibility:public"],
    )
    for version in PYTHON_VERSIONS
]

[
    py_runtime_pair(
        name = "score_bazel_tools_cc_python_{}_runtime_pair".format(version.replace(".", "_")),
        py3_runtime = "@score_bazel_tools_cc_python_{}//:py3_runtime".format(version.replace(".", "_")),
    )
    for version in PYTHON_VERSIONS
]

[
    toolchain(
        name = "score_bazel_tools_cc_python_{}_toolchain".format(version.replace(".", "_")),
        exec_compatible_with = [
            "@platforms//os:linux",
            "@platforms//cpu:x86_64",
        ],
        # Note that target_compatible_with must be empty to ensure that the
        # toolchain resolution will be done only against the execution platform.
        target_compatible_with = [],
        target_settings = [
            ":python_{}".format(version.replace(".", "_")),
            ":use_internal_toolchains",
        ],
        toolchain = ":score_bazel_tools_cc_python_{}_runtime_pair".format(version.replace(".", "_")),
        toolchain_type = "@rules_python//python:toolchain_type",
    )
    for version in PYTHON_VERSIONS
]

#############################################
# Incorrect toolchain configurations traps. #
#############################################

# All code below this comment is related to traps that catch incorrect toolchain configurations.

bool_setting(
    name = "alway_false",
    build_setting_default = False,
)

config_setting(
    name = "never_match",
    flag_values = {":alway_false": "True"},
)

py_runtime_pair(
    name = "py_undefined_pair",
    py3_runtime = select(
        {":never_match": None},
        no_match_error = unsupported_python_configuration_error("Undefined python toolchain error."),
    ),
    tags = ["manual"],  # We do not want to manually build or test this with //...
)

# When the user configures the build incorrectly and none of our Python toolchains matches, this trap will be chosen
# instead of the auto detected non hermetic host toolchain. This will immediately abort the build in the analysis phase
# due to the runtime_pair always hitting and unresolvable select.
toolchain(
    name = "py_undefined_trap",
    target_settings = [
        ":python_undefined",
        ":use_internal_toolchains",
    ],
    toolchain = ":py_undefined_pair",
    toolchain_type = "@rules_python//python:toolchain_type",
)

toolchain(
    name = "do_not_use_internal_toolchains_trap",
    target_settings = [":do_not_use_internal_toolchains"],
    toolchain = ":py_undefined_pair",
    toolchain_type = "@rules_python//python:toolchain_type",
)

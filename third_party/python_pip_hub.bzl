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

"""Load and configure all pip requirements."""

load("@score_bazel_tools_cc//bazel/toolchains/python:versions.bzl", "PYTHON_VERSIONS")
load("@score_bazel_tools_cc_pip_3_10//:requirements.bzl", pip_install_deps_py_3_10 = "install_deps")  # buildifier: disable=out-of-order-load
load("@score_bazel_tools_cc_pip_3_11//:requirements.bzl", pip_install_deps_py_3_11 = "install_deps")  # buildifier: disable=out-of-order-load
load("@score_bazel_tools_cc_pip_3_12//:requirements.bzl", pip_install_deps_py_3_12 = "install_deps")  # buildifier: disable=out-of-order-load
load("@score_bazel_tools_cc_pip_3_8//:requirements.bzl", pip_install_deps_py_3_8 = "install_deps")  # buildifier: disable=out-of-order-load
load("@score_bazel_tools_cc_pip_3_9//:requirements.bzl", pip_install_deps_py_3_9 = "install_deps")  # buildifier: disable=out-of-order-load
load("@bazel_tools_python//bazel/rules:rules_python_pip_hub.bzl", "rules_python_pip_hub")

def python_pip_hub():
    """Load all rules python pip hub and configure our custom pip hub."""

    pip_install_deps_py_3_8()
    pip_install_deps_py_3_9()
    pip_install_deps_py_3_10()
    pip_install_deps_py_3_11()
    pip_install_deps_py_3_12()

    rules_python_pip_hub(
        name = "score_bazel_tools_cc_pip_hub",
        deps_to_config_map = {
            "@score_bazel_tools_cc_pip_{}".format(version.replace(".", "_")): "@score_bazel_tools_cc//bazel/toolchains/python:python_{}".format(version.replace(".", "_"))
            for version in PYTHON_VERSIONS
        },
        requirements_in = "@score_bazel_tools_cc//third_party/pip:requirements.in",
    )

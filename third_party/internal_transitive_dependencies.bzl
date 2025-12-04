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

"""First set of internal transitive dependencies required for this module."""

load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")
load("@buildifier_prebuilt//:defs.bzl", "buildifier_prebuilt_register_toolchains")
load("@buildifier_prebuilt//:deps.bzl", "buildifier_prebuilt_deps")
load("@rules_python//python:repositories.bzl", "py_repositories")
load("@score_bazel_tools_cc//third_party/bazel_tools_python:dep1.bzl", "bazel_tools_python_dep1")
load("@score_bazel_tools_cc//third_party/llvm_toolchain:dep1.bzl", "llvm_toolchain_dep1")

def internal_transitive_dependencies():
    """Load transitive macros of the internal dependencies."""

    bazel_skylib_workspace()
    bazel_tools_python_dep1()
    buildifier_prebuilt_deps()
    buildifier_prebuilt_register_toolchains()
    llvm_toolchain_dep1()
    py_repositories()

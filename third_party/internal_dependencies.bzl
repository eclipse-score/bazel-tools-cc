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

"""Collection of the repository internal thid-party dependencies."""

load("@score_bazel_tools_cc//third_party/bazel_skylib:bazel_skylib.bzl", "bazel_skylib")
load("@score_bazel_tools_cc//third_party/bazel_tools_python:dep0.bzl", "bazel_tools_python_dep0")
load("@score_bazel_tools_cc//third_party/buildifier:buildifier.bzl", "buildifier")
load("@score_bazel_tools_cc//third_party/com_google_protobuf:com_google_protobuf.bzl", "com_google_protobuf")
load("@score_bazel_tools_cc//third_party/llvm_toolchain:dep0.bzl", "llvm_toolchain_dep0")
load("@score_bazel_tools_cc//third_party/rules_cc:rules_cc.bzl", "rules_cc")
load("@score_bazel_tools_cc//third_party/rules_python:rules_python.bzl", "rules_python")

def internal_dependencies():
    """Make internal third-party dependencies known to bazel."""

    bazel_skylib()
    bazel_tools_python_dep0()
    buildifier()
    com_google_protobuf()
    llvm_toolchain_dep0()
    rules_cc()
    rules_python()

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

"""Third-party dependency definition for buildifier."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@score_bazel_tools_cc//bazel:github.bzl", "github_url")

def buildifier():
    http_archive(
        name = "buildifier_prebuilt",
        sha256 = "b0434d14d8ca6eb87ae1d0e71911aeb83ffa3096c6b81db7e26c1698fd980d42",
        strip_prefix = "buildifier-prebuilt-8.2.1",
        url = github_url("keith/buildifier-prebuilt/archive/refs/tags/8.2.1.tar.gz"),
    )

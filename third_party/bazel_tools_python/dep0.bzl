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

"""First level of the third-party dependency definition for bazel-tools-python."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")
load("@score_bazel_tools_cc//bazel:github.bzl", "github_url")

_VERSION = "0.1.3"
_PATH = "eclipse-score/bazel-tools-python/archive/refs/tags/v{version}.tar.gz".format(version = _VERSION)

def bazel_tools_python_dep0():
    maybe(
        http_archive,
        name = "bazel_tools_python",
        sha256 = "8ed81261f513c1f7a2da6ce91e66bb88ccd03532ad7f7ecb08678e56e632f4b1",
        url = github_url(_PATH),
        strip_prefix = "bazel-tools-python-{version}".format(version = _VERSION),
    )

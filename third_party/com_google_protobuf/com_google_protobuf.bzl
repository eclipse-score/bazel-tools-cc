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

"""Third-party dependency definition for com_google_protobuf."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")
load("@score_bazel_tools_cc//bazel:github.bzl", "github_url")

_VERSION = "29.0"
_PATH = "protocolbuffers/protobuf/releases/download/v{version}/protobuf-{version}.tar.gz".format(version = _VERSION)

def com_google_protobuf():
    maybe(
        http_archive,
        name = "com_google_protobuf",
        sha256 = "10a0d58f39a1a909e95e00e8ba0b5b1dc64d02997f741151953a2b3659f6e78c",
        strip_prefix = "protobuf-{version}".format(version = _VERSION),
        url = github_url(_PATH),
    )

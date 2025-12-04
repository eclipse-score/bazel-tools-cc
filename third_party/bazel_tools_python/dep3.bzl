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

"""Fourth level of the third-party dependency definition for bazel-tools-python."""

load("@bazel_tools_python//third_party:python_pip_hub.bzl", bazel_tools_python_python_pip_hub = "python_pip_hub")

def bazel_tools_python_dep3():
    bazel_tools_python_python_pip_hub()

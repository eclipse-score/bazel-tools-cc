#!/bin/bash
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

set -euo pipefail

ABSOLUTE_PATH_TO_YOUR_LOCAL_CLANG_TIDY_BINARY="C:\LLVM\bin\clang"

# Only use case for local non-toolchain clang-tidy versions.
# Expects that clang-tidy is in the $PATH
"${ABSOLUTE_PATH_TO_YOUR_LOCAL_CLANG_TIDY_BINARY}" "${@}"

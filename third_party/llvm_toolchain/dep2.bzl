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

"""Third level of the third-party dependency definition for llvm."""

load("@llvm_toolchain//:toolchains.bzl", "llvm_register_toolchains")

def llvm_toolchain_dep2():
    llvm_register_toolchains()

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

set -eu pipefail

bazel run //third_party/pip:pip_audit_requirements_3_8 || true # Vulnerable packages are expected as python 3.8 is not supported anymore
bazel run //third_party/pip:pip_audit_requirements_3_9
bazel run //third_party/pip:pip_audit_requirements_3_10
bazel run //third_party/pip:pip_audit_requirements_3_11
bazel run //third_party/pip:pip_audit_requirements_3_12

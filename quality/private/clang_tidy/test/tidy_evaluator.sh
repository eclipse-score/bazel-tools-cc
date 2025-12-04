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

# Asserting a string being present in a file
function assert_in() {
  local FILE="${1}"
  local EXPECTED="${2}"
  if cat "${FILE}" | grep "${EXPECTED}"; then
    echo "PASSED: String '${EXPECTED}' in file '${FILE}'"
    return 0
  else
    echo "FAILED: String '${EXPECTED}' in file '${FILE}'"
    echo "Content of '${FILE}' is:"
    cat ${FILE}
    return 1
  fi
}

# Treat template parameter string as an array
EXPECTED_ARRAY=("%EXPECTED%")

# Expect each array value separated by a ";"
IFS=';'

# Loop trough all expected string and check if they are contained in the file
for EXPECTED in ${EXPECTED_ARRAY[@]}; do
  assert_in "%TARGET%" "${EXPECTED}"
done

unset IFS

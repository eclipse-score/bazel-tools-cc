#!/usr/bin/env bash
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

set -u

GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

BZL_WORSKPACE_OUTPUT_BASE="$HOME/.cache/score_bazel_tools_cc_tests/workspace_output_base"


declare -A command_status
declare -a command_order
exit_code=0


interrupt_handler(){
	echo -e "${RED}Script interrupted by user.${RESET}"
	exit 130	# Exit code for script interruption by Ctrl+C
}

trap interrupt_handler SIGINT

run_command(){
	local cmd=$1
	local name=$2

	echo -e "Running $name ..."

	if eval "$cmd"; then
		echo -e "${GREEN}$name SUCCEEDED${RESET}"
		command_status["$name"]="SUCCEEDED"
	else
		echo -e "${RED}$name FAILED${RESET}"
		command_status["$name"]="FAILED"
		exit_code=1
	fi

	command_order+=("$name")
}

# Ensure the following commands are run from the test workspace.
cd $(dirname $0)

# Run checks with bzlmod mode.
run_command "bazel test //..." "tests (bzlmod mode)"
run_command "bazel build --config=clang_tidy --keep_going //..." "clang-tidy exit 0 (bzlmod mode)"
run_command "bazel build --config=clang_tidy --features=treat_clang_tidy_warnings_as_errors //...; [ \$? -eq 1 ]" "clang_tidy exit 1 (bzlmod mode)"
run_command "bazel build --config=clang_format --keep_going //..." "clang-format (bzlmod mode)"

# Run checks in workspace mode
run_command "bazel --output_base=${BZL_WORSKPACE_OUTPUT_BASE} test --config=use_workspace_mode //..." "tests (workspace mode)"
run_command "bazel --output_base=${BZL_WORSKPACE_OUTPUT_BASE} build --config=use_workspace_mode --config=clang_tidy --keep_going //..." "clang-tidy exit 0 (workspace mode)"
run_command "bazel --output_base=${BZL_WORSKPACE_OUTPUT_BASE} build --config=use_workspace_mode --config=clang_tidy --features=treat_clang_tidy_warnings_as_errors //...; [ \$? -eq 1 ]" "clang-tidy exit 1 (workspace mode)"
run_command "bazel --output_base=${BZL_WORSKPACE_OUTPUT_BASE} build --config=use_workspace_mode --config=clang_format --keep_going //..." "clang-format (workspace mode)"

# Print execution summary
printf '%-37s | %-10s\n' "Command Name" "Status"
printf '%-37s | %-10s\n' "-------------------------------------" "----------"

for name in "${command_order[@]}"; do
	status="${command_status[$name]}"

	if [[ "$status" == "SUCCEEDED" ]]; then
		printf "%-37s | ${GREEN}%-10s${RESET}\n" "$name" "$status"
	else
		printf "%-37s | ${RED}%-10s${RESET}\n" "$name" "$status"
	fi
done

printf '%-37s | %-10s\n' "-------------------------------------" "----------"

exit $exit_code

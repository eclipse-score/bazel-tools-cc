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


declare -A command_status
declare -a command_order
exit_code=0
[ $# -gt 0 ] && workspace=$1 || workspace="all"


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

if [ "${workspace}" == "all" -o "${workspace}" == "main" ];then
	# Run bazel test with workspace mode and python 3.9.
	# TODO re-enable once the score targets (like //:docs) support bazel workspace mode and more than python 3.12
	# run_command "bazel --output_base=$HOME/.cache/bazel_tools_cc/workspace_output_base test --config=use_workspace_mode --config=python_3_9 //..." "tests (workspace mode and python 3.9)"

	# Run bazel test with bzlmod mode and python 3.12.
	run_command "bazel --output_base=$HOME/.cache/bazel_tools_cc/python_3_12_output_base test --config=python_3_12 //..." "tests (bzlmod mode and python 3.12)"

	# Run bazel test with bzlmod mode.
	run_command "bazel test //..." "tests (bzlmod mode)"

	# Run bazel test with bzlmod and experimental_cc_implementation_deps
	targets=" \
		//quality/private/clang_tidy/test:tidy_no_finding_in_implementation_deps_test \
		//quality/private/clang_tidy/test:tidy_one_finding_in_implementation_deps_test \
		//quality/private/clang_tidy/test:tidy_one_finding_in_header_implementation_deps_test \
		//quality/private/clang_tidy/test:tidy_special_finding_within_ifdef_of_header_implementation_deps_test
	"

	run_command "bazel test --experimental_cc_implementation_deps -- ${targets}" "tests (bzlmod mode with experimental_cc_implementation_deps)"

	# Run clang-format
	run_command "bazel build --config=clang_format --keep_going //..." "clang-format"

	# Run python quality tools.
	run_command "bazel build --config=ruff_check --keep_going //..." "ruff_check"
	run_command "bazel build --config=ruff_format --keep_going //..." "ruff_format"
	run_command "bazel build --config=pylint --keep_going //..." "pylint"
	run_command "bazel build --config=black --keep_going //..." "black"
	run_command "bazel build --config=isort --keep_going //..." "isort"
	run_command "bazel build --config=mypy --keep_going //..." "mypy"

	# Run buildifier.
	run_command "bazel run bazel/buildifier:check" "buildifier"

	# Run Eclipse-specific checks.
	run_command "bazel run //:copyright.check -- --fix" "eclipse copyright check"

	# Run security vulnerability scan.
	run_command "third_party/pip/check_vulnerabilities.sh" "security scan"
fi

if [ "${workspace}" == "all" -o "${workspace}" == "test" ];then
	# Run test workspace tests.
	run_command "test/run_all_tests.sh" "tests (in test workspace)"
fi

if [ "${workspace}" == "all" -o "${workspace}" == "main" ];then
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
fi

exit $exit_code

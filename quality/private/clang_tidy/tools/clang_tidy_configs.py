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

"""
Module to assert clang-tidy configs, e.g. merging multiple configs into one.
"""

import logging
import typing as t
from collections import defaultdict

import termcolor

from quality.private.clang_tidy.tools import common


def assert_keys(merged_dict: dict, input_dict: dict) -> None:
    """Asserts root level keys of a clang tidy config."""
    for key, value in input_dict.items():
        is_string = False
        count_string_lists = 0
        separated_values_comma = set()
        separated_values_semicolon = set()

        for value_probe in value:
            # We do not have a string at all
            is_string = is_string or isinstance(value_probe, str)
            if is_string:
                separated_values_comma |= prepare_string_set(value_probe, ",")
                separated_values_semicolon |= prepare_string_set(value_probe, ";")

                # We do not have a list like string
                if len(separated_values_comma) > 1 or len(separated_values_semicolon) > 1:
                    count_string_lists += 1

        if not is_string or (is_string and count_string_lists == 0):
            assert_uniqueness(merged_dict, key, value)
        elif count_string_lists == len(value):
            merged_values_comma = merge_strings(list(separated_values_comma), ",")
            merged_values_semicolon = merge_strings(list(separated_values_semicolon), ";")
            merged_dict[key] = merged_values_comma + merged_values_semicolon
        else:
            logging.error(
                termcolor.colored(
                    "Conflict: Either all or none CheckOptions must be of type list. A mix is not allowed.",
                    "red",
                )
            )
            raise common.ConfigException(message="TypesMismatch")


def merge_strings(separated_values: t.Iterable[str], separator: str) -> str:
    """Sorts and merges the unique strings from a list using `separator` between each of them."""
    unique_separated_values = set(filter(None, separated_values))
    return separator.join(sorted(list(unique_separated_values)) + [""])


def prepare_string_set(value_probe: str, separator: str) -> set:
    """Prepares a string set by splitting `value_probe` using `separator` as the separator string."""
    split = set(value_probe.split(separator))
    # In cases the "split" would result in only one element
    # which is the behavior when you have "foo" which will become set("foo"),
    # we ignore it and return an empty set to indicate that we do
    # not have a list, but a normal string.
    return split if len(split) > 1 else set()


def assert_uniqueness(merged_dict: dict, key: str, value: list) -> None:
    """Asserts a key is unique."""
    is_unique = len(set(value)) == 1
    if not is_unique:
        logging.error(
            termcolor.colored(
                f"Conflict: For key `{key}` all values must be exactly the same among all configs.",
                "red",
            )
        )
        raise common.ConfigException(message="Uniqueness")
    merged_dict[key] = value[0]


def assert_options(merged_config: dict, options: dict) -> None:
    """Asserts options are always the same."""
    merged_options = {}
    assert_keys(merged_options, options)
    merged_config["CheckOptions"] = [{"key": k, "value": v} for k, v in merged_options.items()]


def reduce_checks(checks: set) -> set:
    """Merges two equal checks, i.e. if one check is contained in the other one via wildcards."""
    remove_checks = set()
    for wildcard_check in checks:
        if wildcard_check.endswith("*"):
            for check in checks:
                if check.startswith(wildcard_check[:-1]) and check != wildcard_check:
                    remove_checks.add(check)
    return checks - remove_checks


def assert_checks(merged_config: dict, activated_checks: set, deactivated_checks: set) -> None:
    """Asserts checks are not activated and deactivated at the same time."""
    activated_checks = reduce_checks(activated_checks)

    assert_check_conflict(activated_checks, deactivated_checks)
    assert_check_wildcard_conflict(activated_checks, deactivated_checks)

    deactivated_checks = reduce_checks(deactivated_checks)

    activated_checks_list = sorted(list(activated_checks))
    deactivated_checks_list = [f"-{check}" for check in sorted(list(deactivated_checks))]

    merged_config["Checks"] = ",".join(deactivated_checks_list + activated_checks_list)


def assert_check_conflict(activated_checks: set, deactivated_checks: set) -> None:
    """Asserts conflicts in activated checks."""
    activated_and_deactivated_checks = set.intersection(activated_checks, deactivated_checks)
    if len(activated_and_deactivated_checks):
        logging.error(
            termcolor.colored(
                "Conflict: A check cannot be activated and deactivated at the same time."
                f"\nConflicting checks are: {activated_and_deactivated_checks}",
                "red",
            )
        )
        raise common.ConfigException(message="CheckConflict")


def assert_check_wildcard_conflict(activated_checks: set, deactivated_checks: set) -> None:
    """
    Special case when "-*" is been used (and the CheckOrderConflict has already checked
    that this comes before the activated checks). This is "ok" to be in conflict as the
    intention is usually to deactivated the default activated ones before specifying the
    ones to activate.
    """
    deactivated_checks_without_star = deactivated_checks.copy()
    if "*" in deactivated_checks_without_star:
        deactivated_checks_without_star.remove("*")

    before = activated_checks | reduce_checks(deactivated_checks_without_star)
    after = reduce_checks(before)

    if len(before) - len(after) != 0:
        logging.error(
            termcolor.colored(
                "Conflict: A check cannot be activated and deactivated at the same time."
                " Note: A wildcard `*` has been resolved and leads to this conflict."
                f"\nConflicting checks are: {before - after}",
                "red",
            )
        )
        raise common.ConfigException(message="CheckWildcardConflict")


def process_checks(activated_checks: set, deactivated_checks: set, value: str) -> None:
    """Process a single check."""
    has_seen_activated_check = False

    for check in value.strip().split(","):
        check = check.strip()
        if not check:
            continue

        if check.startswith("-"):
            if has_seen_activated_check:
                logging.error(termcolor.colored("All deactivated checks must come before the activated ones.", "red"))
                raise common.ConfigException(message="CheckOrderConflict")
            deactivated_checks.add(check[1:])
        else:
            has_seen_activated_check = True
            activated_checks.add(check)


def merge_configs(configs: list) -> dict:
    """Main entry point to merge multiple configs."""
    merged_config = {}

    activated_checks = set()
    deactivated_checks = set()

    options = defaultdict(list)
    other_keys = defaultdict(list)

    if len(configs) == 1:
        return configs[0]

    for config in configs:
        for key, value in config.items():
            if key == "Checks":
                process_checks(activated_checks, deactivated_checks, value)
            elif key == "CheckOptions":
                for option in value:
                    options[option["key"]].append(option["value"])
            else:
                other_keys[key].append(value)

    assert_keys(merged_config, other_keys)
    assert_checks(merged_config, activated_checks, deactivated_checks)
    assert_options(merged_config, options)

    return merged_config

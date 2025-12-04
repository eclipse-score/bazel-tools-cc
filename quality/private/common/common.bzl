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

"""A collection of utility functions to be used throughout the project."""

def is_windows_os(ctx):
    """Returns true if the host operating system is Windows."""
    return ctx.configuration.host_path_separator == ";"

def path_starts_with(pattern, src):
    """Check whether the src path start with the given pattern or not.

    Args:
        pattern: A string containing the path pattern.
        src: The source file object.
    Returns:
        True if src path starts with the given pattern, otherwise False.
    """
    if src.path.startswith(pattern):
        return True
    if hasattr(src, "short_path"):
        return src.short_path.startswith(pattern)
    return False

def is_valid_target_filter(excludes, excludes_override, src):
    """Controls whether to analyze a give source file or not, based on exclusion and inclusion lists.

    Args:
        excludes: A list of path names (string) to exclude.
        excludes_override: A list of path names (string) to include nonetheless.
        src: The source file.
    Returns:
        False if src starts with any path from excludes but not any path from excludes_override.
    """
    for inclusion in excludes_override:
        if path_starts_with(inclusion, src):
            return True
    for exclusion in excludes:
        if path_starts_with(exclusion, src):
            return False
    return True

def is_feature_active(ctx, feature_name, extra_features = []):
    """Determines if a feature is active in a generic way.

    Args:
        ctx: Bazel context.
        feature_name: name of the feature to check.
        extra_features: (Optional) A list of extra enabled features from tool config.
    Returns:
        True if feature is active, False otherwise.
    """
    return (
        feature_name in ctx.features or
        feature_name in ctx.rule.attr.features or
        feature_name in extra_features
    )

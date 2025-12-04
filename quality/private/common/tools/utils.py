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

"""Module for some utils that may be used by all other modules."""

import logging
import sys
from pathlib import Path

import jsonschema
import yaml


def escape_quotes(arguments):
    """
    Escape quotes:
    Some arguments use double backslashes for escaping quotes,
    whichc has to be resolved before the argument can be used by tools
    like clang-tidy and iwyu.
    """
    return arguments.replace('\\"', '"')


def read_and_validate_yaml_file(yaml_file: Path, schema: dict) -> dict:
    """Read and validate a yaml file using a schema, then, return its content as a dict."""
    with yaml_file.open(mode="r", encoding="UTF-8") as stream:
        try:
            content = yaml.safe_load(stream)
            jsonschema.validate(content, schema)
        except yaml.YAMLError as exc:
            logging.error("Invalid YAML file format\n%s", exc)
            sys.exit(1)
        except jsonschema.exceptions.ValidationError as exc:
            logging.error("The YAML doesn't met the schema validation\n%s", exc)
            sys.exit(1)
    return content


class ParseError(Exception):
    """An error when parsing a file.

    In addition to its parent exception, a ParseError contains
    two extra attributes.

    Args:
        msg (str): The error message.
        file_path (str): The respective file path.
    """

    def __init__(self, msg: str, file_path: str):
        super().__init__(msg)
        self.msg = msg
        self.file_path = file_path

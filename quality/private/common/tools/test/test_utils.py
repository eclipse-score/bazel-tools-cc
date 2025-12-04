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

"""Tests for the utils file."""

import shutil
import tempfile
import unittest
from pathlib import Path

from quality.private.common.tools.utils import read_and_validate_yaml_file


class TestUtils(unittest.TestCase):
    """Common utils test class, its setup provides a temp_dir with mock files."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()

        self.schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "data": {
                    "type": "integer",
                },
            },
            "required": [
                "data",
            ],
        }

        self.expected_dict = {"data": 1}

        self.valid_yaml = Path(self.temp_dir, "valid.yaml")
        self.valid_yaml.write_text(r'{"data": 1}', encoding="utf-8")

        self.invalid_schema_yaml = Path(self.temp_dir, "invalid_schema.yaml")
        self.invalid_schema_yaml.write_text(r'{"data": 1.1}', encoding="utf-8")

        self.invalid_yaml = Path(self.temp_dir, "invalid.yaml")
        self.invalid_yaml.write_text(r'{"data" 1}', encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_read_and_validate_yaml_file(self):
        """Test the read_and_validate_yaml_file happy and bad paths, the arrange phase is done by the setup."""
        output_dict = read_and_validate_yaml_file(self.valid_yaml, self.schema)

        self.assertEqual(output_dict, self.expected_dict)

        with self.assertRaises(SystemExit) as sys_exc:
            read_and_validate_yaml_file(self.invalid_yaml, self.schema)
        self.assertNotEqual(sys_exc.exception.code, 0)

        with self.assertRaises(SystemExit) as sys_exc:
            read_and_validate_yaml_file(self.invalid_schema_yaml, self.schema)
        self.assertNotEqual(sys_exc.exception.code, 0)

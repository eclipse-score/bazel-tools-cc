/********************************************************************************
 * Copyright (c) 2025 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

#ifndef BAZEL_TOOLS_CLANG_TIDY_EXAMPLES_EXAMPLE_H
#define BAZEL_TOOLS_CLANG_TIDY_EXAMPLES_EXAMPLE_H

#include <cstdint>

namespace project {
namespace tidy_suite {

using namespace project;  // NOLINT

void Bugprone(bool bug);
std::int32_t Example();

}  // namespace tidy_suite
}  // namespace project

#endif  // BAZEL_TOOLS_CLANG_TIDY_EXAMPLES_EXAMPLE_H

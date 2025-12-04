workspace(name = "score_bazel_tools_cc")

########################
# Direct dependencies. #
########################

load("@score_bazel_tools_cc//third_party:dependencies.bzl", "dependencies")

dependencies()

##########################
# Internal dependencies. #
##########################

load("@score_bazel_tools_cc//third_party:internal_dependencies.bzl", "internal_dependencies")

internal_dependencies()

load("@score_bazel_tools_cc//third_party:internal_transitive_dependencies.bzl", "internal_transitive_dependencies")

internal_transitive_dependencies()

load("@score_bazel_tools_cc//third_party:internal_transitive_dependencies1.bzl", "internal_transitive_dependencies1")

internal_transitive_dependencies1()

load("@score_bazel_tools_cc//third_party:internal_transitive_dependencies2.bzl", "internal_transitive_dependencies2")

internal_transitive_dependencies2()

######################################
# Python toolchain and dependencies. #
######################################

load("@score_bazel_tools_cc//third_party:python_toolchains.bzl", "python_toolchains")

python_toolchains()

load("@score_bazel_tools_cc//bazel/toolchains:toolchains.bzl", "toolchains")

toolchains()

load("@score_bazel_tools_cc//third_party:python_pip_parse.bzl", "python_pip_parse")

python_pip_parse()

load("@score_bazel_tools_cc//third_party:python_pip_hub.bzl", "python_pip_hub")

python_pip_hub()

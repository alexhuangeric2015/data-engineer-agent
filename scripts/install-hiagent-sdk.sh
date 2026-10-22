#!/usr/bin/env bash
set -euo pipefail

# 官方 SDK 3.1.0 尚未在 Maven Central 发布，本脚本从指定提交安装知识库模块到本机 Maven 缓存。
SDK_REPOSITORY='https://github.com/volcengine/hiagent-java-sdk.git'
SDK_REVISION='f42b1ebf3b2859ba17f8be92a996fba6c2d084d3'
SDK_DIRECTORY="$(mktemp -d)"
trap 'rm -rf "$SDK_DIRECTORY"' EXIT

git clone --quiet "$SDK_REPOSITORY" "$SDK_DIRECTORY"
git -C "$SDK_DIRECTORY" checkout --quiet "$SDK_REVISION"
mvn -q -f "$SDK_DIRECTORY/pom.xml" -pl hiagent-api -am install -DskipTests

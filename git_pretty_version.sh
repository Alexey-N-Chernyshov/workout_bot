#!/bin/sh
set -e

GIT_REPO_PRETTY_VERSION=$(git describe --tags --always --dirty) || GIT_REPO_PRETTY_VERSION="git-unknown"
echo "$GIT_REPO_PRETTY_VERSION" > git_commit_version.txt

#!/bin/bash
# usage: run.sh <case-dir> ; runs kyverno test on both pinned engines, prints table + rc
# BIN holds bin/1.18.2/kyverno and bin/1.19.1/kyverno (the pinned darwin_arm64 CLIs).
S=${BIN:?set BIN to the directory that holds bin/<version>/kyverno}
for v in 1.18.2 1.19.1; do
  echo "### kyverno $v: \$ kyverno test $1 --remove-color"
  out=$("$S/bin/$v/kyverno" test "$1" --remove-color 2>&1); rc=$?
  printf '%s\n' "$out" | grep -v '^\s*Loading'
  echo "# rc=$rc"
done

#!/bin/zsh
V=<scratch>/verify
for d in "$@"; do for ver in 1.18.2 1.19.1; do
  out=$($V/bin/$ver/kyverno test $V/min/$d --remove-color 2>&1); rc=$?
  print -r -- "## $d on $ver (exit $rc)"
  print -r -- "$out" | grep -E "^│ [0-9]|Test Summary|Error|rror" 
done; done

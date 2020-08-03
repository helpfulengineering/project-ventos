#!/bin/bash
echo "starting will run '$2' on any change to '$1'"
inotifywait -mr -e close_write $1 |
while read D E F; do
  # echo "----------------hello $D $E $F"
  if [[ "$F" == *.py || "$F" == *.yaml ]]
  then
    echo "starting"
    eval "$2"
    echo "done"
  fi
done

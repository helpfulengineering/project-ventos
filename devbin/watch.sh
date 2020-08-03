#!/bin/bash
echo "Starting watch. Will run '$2' on any change to '$1'"
echo "Note only watching .py and .yaml files currently."
echo "Edit this script to watch other file types."
inotifywait -mr -e close_write $1 |
while read D E F; do
  # echo "----------------hello $D $E $F"
  if [[ "$F" == *.py || "$F" == *.yaml ]]
  then
    echo "Doing: $2"
    eval "$2"
    echo "Done"
  fi
done

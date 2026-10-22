#!/bin/sh

# Arah: this script is disabled on purpose.
echo "Arah keeps its own FAQ in data/faq.html; this script would replace it with upstream's. Edit data/faq.html directly." >&2
exit 1

SCRIPT_DIR=$(dirname -- "${BASH_SOURCE[0]}")
OUTPUT_FILE="$SCRIPT_DIR/../../data/faq.html"

echo "Downloading latest FAQ page from organicmaps.app website ..."
curl -s -L -f -o $OUTPUT_FILE https://organicmaps.app/faq/embedded-faq

res=$?
if test "$res" != "0"; then
   echo "The curl command failed with: $res"
else
   echo "Success!"
fi

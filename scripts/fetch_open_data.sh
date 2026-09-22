#!/usr/bin/env sh
# Fetch the Impect open data used by the mock API (and the whole pipeline).
set -e
cd "$(dirname "$0")/.."
if [ ! -d source_data/.git ]; then
  git clone --depth 1 https://github.com/ImpectAPI/open-data.git source_data
fi
echo "Data ready in source_data/ ($(ls source_data/data/events | wc -l) event files)"

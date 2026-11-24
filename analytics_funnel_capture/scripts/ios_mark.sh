#!/usr/bin/env bash
# Label the funnel step you're on in the app. Usage: scripts/ios_mark.sh "onboarding 2"
cd "$(dirname "$0")/.."
mkdir -p data
echo "${1:?usage: ios_mark.sh <step label>}" > data/ios_step.txt
echo "step -> $1"

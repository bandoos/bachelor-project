#!/bin/bash
perl -pe 's/((?<=,)|(?<=^)),/ ,/g;' | column -t -s, | less -S

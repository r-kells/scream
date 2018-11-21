#!/usr/bin/env sh

git show-branch -a \
| grep '\*' \
| grep -v `git rev-parse --abbrev-ref HEAD` \
| head -n1 \
| sed 's/.*\[\(.*\)\].*/\1/' \
| sed 's/[\^~].*//'

# How it works:
# 1| Display a textual history of all commits.
# 2| Ancestors of the current commit are indicated
#    by a star. Filter out everything else.
# 3| Ignore all the commits in the current branch.
# 4| The first result will be the nearest ancestor branch.
#    Ignore the other results.
# 5| Branch names are displayed [in brackets]. Ignore
#    everything outside the brackets, and the brackets.
# 6| Sometimes the branch name will include a ~2 or ^1 to
#    indicate how many commits are between the referenced
#    commit and the branch tip. We don't care. Ignore them.#!/usr/bin/env bash
#!/bin/bash
 
# Adapted from a puppet pre-commit hook at:
# http://blog.snijders-it.nl/2011/12/example-puppet-27-git-pre-commit-script.html
#
# install this as .git/hooks/pre-commit to check DNS zone files
# for errors before committing changes.
 
rc=0
 
[ "$SKIP_PRECOMMIT_HOOK" = 1 ] && exit 0
 
# Make sure we're at top level of repository.
cd $(git rev-parse --show-toplevel)
 
trap 'rm -rf $tmpdir $tmpfile1' EXIT INT HUP
tmpdir=$(mktemp -d precommitXXXXXX)
tmpfile1=$(mktemp errXXXXXX)
 
echo "$(basename $0): Validating changes."
 
# Here we copy files out of the index into a temporary directory. This
# protects us from a the situation in which we have staged an invalid
# zone file using ``git add`` but corrected the changes in the
# working directory. If we checked the files "in place", we would
# fail to detect the errors.
 
git diff-index --cached --name-only HEAD |
grep '^zones/' |
git checkout-index --stdin --prefix=$tmpdir/
 
find $tmpdir/zones -type f |
while read zonefile; do
    zone=`echo $zonefile | sed -e "s/^${tmpdir}\/zones\/\(.*\)$/\1/"`
    named-checkzone -q $zone $zonefile
    # If named-checkzone reports an error, get some output:
    if [ $? -ne 0 ]; then
    named-checkzone $zone $zonefile | sed "s#$tmpdir/##" >> $tmpfile1 2>&1
    fi
done
 
if [ -s "$tmpfile1" ]; then
echo
echo Error: Zone file problem:
echo ----------------------------
cat $tmpfile1
echo ----------------------------
echo
 
rc=1
fi
 
exit $rc

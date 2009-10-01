#!/bin/sh
diff --strip-trailing-cr -us $1 $2
exit $?
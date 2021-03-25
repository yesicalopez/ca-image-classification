#!/bin/bash

# pre-downloaded files for select stations from jervis archive into local dir with
# wget -r --no-parent --no-directories -A jpg http://jervis.pyr.ec.gc.ca/archive_db/<YYYYMM>/<YYYYMM>{<DD>..<DD>}/RVAS/<TCID>/<optional if only one camera direction desired>/
# e.g. wget -r --no-parent --no-directories -A jpg http://jervis.pyr.ec.gc.ca/archive_db/202102/202102{01..28}/RVAS/VOO/NW/
# note the ending / in the url above is very important for the recursion no parent to work

# download all the stations in stations.txt for the given YYYYMM
# e.g run ./download_from_jervis.sh stations.txt 202102

LOG_DF="%Y-%m-%dT%H:%M:%S,%3NZ"

stations_file=$1
yyyymm=$2
output_dir="/apps/dms/ca-images/all/"

if [ -f "$stations_file" ] ; then
    echo "[$(date +${LOG_DF})] [Reading config file $stations_file]"
    while read line
    do
        if [ -n "$line" ] ; then
            wget -r --no-parent -P "$output_dir" --no-directories -A jpg http://jervis.pyr.ec.gc.ca/archive_db/"$yyyymm"/"$yyyymm"{01..31}/RVAS/"$line"/
        fi
    done < "$stations_file"
else
    echo "[$(date +${LOG_DF})] [Unable to create trigger files due to missing configuration file: $stations_file]"
    exit 1
fi

exit 0



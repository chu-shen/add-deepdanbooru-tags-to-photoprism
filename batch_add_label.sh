#!/bin/bash

add_labels_to_photoprism() {
  # session_id=api._create_session('admin','adminadmin')['id']
  temp=$(curl -s --compressed --request POST "http://192.168.3.8:2342/api/v1/photos/$1/label" \
    --header 'X-Session-ID: REPLACE_Session_ID' \
    --header 'Content-Type: application/json' \
    --data-raw '{
    "Name": "'$2'",
    "Source": "manual",
    "Uncertainty": '$3',
    "Priority": 10
  }')
}

process_photo_labels() {
  filename=$(basename $1)
  photo_uid=${filename%%.*}

  while IFS=, read -ra line; do
    {
      score=$(echo "${line[1]}" | awk '{printf("%.0f",(1-$1)*100)}')
      add_labels_to_photoprism $photo_uid ${line[0]} $score
    } &
  done <$1

  wait
}

process_photos() {
  THREAD_NUM=50
  SIFIFO="photos_fifo"
  # mkfifo in QNAP
  /share/CACHEDEV1_DATA/.qpkg/MediaSignPlayer/CodexPackExt/usr/bin/mkfifo ${SIFIFO}

  exec 6<>${SIFIFO}
  rm -f "${SIFIFO}"

  for ((i = 1; i <= ${THREAD_NUM}; i++)); do
    {
      echo
    }
  done >&6

  for photo in ./tag_score/*.txt; do
    {
      read -u6
      {
        [[ -e "$photo" ]] || break # handle the case of no *.txt files
        echo $photo
        process_photo_labels $photo
        echo "" >&6
      } &
    }
  done

  wait
  exec 6>&-
}

starttime=$(date +'%Y-%m-%d %H:%M:%S')
process_photos

endtime=$(date +'%Y-%m-%d %H:%M:%S')
start_seconds=$(date --date="$starttime" +%s)
end_seconds=$(date --date="$endtime" +%s)
echo "本次运行时间： "$((end_seconds - start_seconds))"s"

#!/bin/bash
while read -r url; do
    status=$(curl -o /dev/null -s -L -w "%{http_code}" "$url")
    if [ "$status" = "200" ]; then
        echo "$url" >> clean.txt
    fi
done < sources.txt

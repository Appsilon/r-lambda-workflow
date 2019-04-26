#!/bin/sh

while true
do
  HEADERS="$(mktemp)"

  EVENT_DATA=$(curl -sS -LD "$HEADERS" -X GET "http://${AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/next")
  REQUEST_ID=$(grep -Fi Lambda-Runtime-Aws-Request-Id "$HEADERS" | tr -d '[:space:]' | cut -d: -f2)

  RESPONSE=$(/opt/R/bin/Rscript /opt/runtime.R $EVENT_DATA)
  RESPONSE_CODE=$?

  if [ $RESPONSE_CODE = 0 ]; then
    OUT="response"
  elif [ $RESPONSE_CODE = 100 ]; then
    OUT="error"
  fi

  curl -X POST "http://${AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/$REQUEST_ID/$OUT" -d "$RESPONSE"
done

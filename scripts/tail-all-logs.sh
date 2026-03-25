#!/bin/bash
# Tail all service logs together with service name prefix

DATE=$(date +%Y%m%d)
LOGS_DIR="../logs"

# Find today's log files
FRONTEND_LOG="${LOGS_DIR}/log-frontend-${DATE}.json"
BACKEND_LOG="${LOGS_DIR}/log-backend-${DATE}.json"
LANGCHAIN_LOG="${LOGS_DIR}/log-langchain-${DATE}.json"
FASTMCP_LOG="${LOGS_DIR}/log-fastmcp-${DATE}.json"

# Create logs directory if it doesn't exist
mkdir -p "${LOGS_DIR}"

# Tail all logs with service prefix
tail -f \
  "${FRONTEND_LOG}" 2>/dev/null | sed 's/^/[FRONTEND] /' &
  "${BACKEND_LOG}" 2>/dev/null | sed 's/^/[BACKEND] /' &
  "${LANGCHAIN_LOG}" 2>/dev/null | sed 's/^/[LANGCHAIN] /' &
  "${FASTMCP_LOG}" 2>/dev/null | sed 's/^/[FASTMCP] /' &

# Wait for all background processes
wait

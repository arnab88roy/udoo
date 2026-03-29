#!/bin/bash

# Udoo Frontend Dev Entrypoint
# This script handles log rotation to prevent TD-18 (log bloat)

LOG_FILE="next.log"
MAX_SIZE_MB=10
MAX_SIZE_BYTES=$((MAX_SIZE_MB * 1024 * 1024))

# Ensure we are in the frontend directory
cd "$(dirname "$0")/.."

# Check if log file exists and exceeds limit
if [ -f "$LOG_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null)
    
    if [ "$FILE_SIZE" -gt "$MAX_SIZE_BYTES" ]; then
        echo "[LOG ROTATION] Truncating $LOG_FILE ($((FILE_SIZE / 1024 / 1024))MB > ${MAX_SIZE_MB}MB)"
        # Keep only the last 1MB of the log to preserve recent context
        tail -c 1048576 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
    fi
fi

echo "[UDOO] Starting Next.js Dev Server (Logs: $LOG_FILE)"

# Execute next dev and pipe to log file while still showing in stdout
# Using tee to ensure logs are captured but visibility is maintained
exec npx next dev 2>&1 | tee -a "$LOG_FILE"

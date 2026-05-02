#!/bin/bash
# Usage: ./set_time.sh <hour> [minute]
# Example: ./set_time.sh 23       → runs at 23:00
# Example: ./set_time.sh 9 30     → runs at 09:30

HOUR=${1:?Usage: ./set_time.sh <hour> [minute]}
MINUTE=${2:-0}
PLIST=~/Library/LaunchAgents/com.dsalock.plist

/usr/libexec/PlistBuddy -c "Set :StartCalendarInterval:Hour $HOUR" "$PLIST"
/usr/libexec/PlistBuddy -c "Set :StartCalendarInterval:Minute $MINUTE" "$PLIST"

launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"

echo "DSA Lock scheduled for $(printf '%02d:%02d' $HOUR $MINUTE) daily."

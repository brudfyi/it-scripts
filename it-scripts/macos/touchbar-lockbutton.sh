#!/usr/bin/env bash
#
#

# Get the Username of the currently logged user
loggedInUser=`/bin/ls -l /dev/console | /usr/bin/awk '{ print $3 }'`
echo Disabling siri button, adding screen lock button to touchbar for user: $loggedInUser
##Set control strip for user
#full
sudo -u $loggedInUser rm ~/Library/Preferences/com.apple.controlstrip.plist
sudo -u $loggedInUser defaults write com.apple.controlstrip FullCustomized -array-add com.apple.system.group.brightness
sudo -u $loggedInUser defaults write com.apple.controlstrip FullCustomized -array-add com.apple.system.mission-control
sudo -u $loggedInUser defaults write com.apple.controlstrip FullCustomized -array-add com.apple.system.launchpad
sudo -u $loggedInUser defaults write com.apple.controlstrip FullCustomized -array-add com.apple.system.group.keyboard-brightness
sudo -u $loggedInUser defaults write com.apple.controlstrip FullCustomized -array-add com.apple.system.group.media
sudo -u $loggedInUser defaults write com.apple.controlstrip FullCustomized -array-add com.apple.system.group.volume
sudo -u $loggedInUser defaults write com.apple.controlstrip FullCustomized -array-add com.apple.system.screen-lock
#mini
sudo -u $loggedInUser defaults write com.apple.controlstrip MiniCustomized -array-add com.apple.system.brightness
sudo -u $loggedInUser defaults write com.apple.controlstrip MiniCustomized -array-add com.apple.system.volume
sudo -u $loggedInUser defaults write com.apple.controlstrip MiniCustomized -array-add com.apple.system.mute
sudo -u $loggedInUser defaults write com.apple.controlstrip MiniCustomized -array-add com.apple.system.screen-lock
killall ControlStrip
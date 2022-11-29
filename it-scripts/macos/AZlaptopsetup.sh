#!/bin/sh

###
#
#   █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ███╗███████╗███████╗███╗   ██╗
#  ██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║╚══███╔╝██╔════╝████╗  ██║
#  ███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║  ███╔╝ █████╗  ██╔██╗ ██║
#  ██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║ ███╔╝  ██╔══╝  ██║╚██╗██║
#  ██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║███████╗███████╗██║ ╚████║
#  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝
#
#         ╦╔╗╔╦╔╦╗╦╔═╗╦    ╦  ╔═╗╔═╗╔╦╗╔═╗╔═╗  ╔═╗╔═╗╔╦╗╦ ╦╔═╗
#         ║║║║║ ║ ║╠═╣║    ║  ╠═╣╠═╝ ║ ║ ║╠═╝  ╚═╗║╣  ║ ║ ║╠═╝
#         ╩╝╚╝╩ ╩ ╩╩ ╩╩═╝  ╩═╝╩ ╩╩   ╩ ╚═╝╩    ╚═╝╚═╝ ╩ ╚═╝╩  
#
###
echo "Loading...................................."
sleep 1
echo "Hold on..."
sleep 1
echo "Here we go..."
sleep 1
echo "Feel the rhythm!"
sleep 1
echo "Feel the rhyme!"
sleep 1
echo "Get on up, it's bobsled time!"
sleep 2
echo "Cool Runnings!"


if ! command -v brew >/dev/null; then
    echo "Installing brew..."
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

if ! command -v git >/dev/null; then
    echo "Installing Git..."
    brew install git
fi 

echo "Installing brew cask..."
brew tap caskroom/cask

echo "finished installing brew cask."

echo "Installing dockutil..."
brew install dockutil 

###
#  ╔═╗╔═╗╦  ╦  ╔═╗╔╗ ╔═╗╦═╗╔═╗╔╦╗╦╔═╗╔╗╔
#  ║  ║ ║║  ║  ╠═╣╠╩╗║ ║╠╦╝╠═╣ ║ ║║ ║║║║
#  ╚═╝╚═╝╩═╝╩═╝╩ ╩╚═╝╚═╝╩╚═╩ ╩ ╩ ╩╚═╝╝╚╝
###
echo "Installing collaboration applications..."
if ! open -Ra "Discord">/dev/null; then brew cask install discord; fi
if ! open -Ra "Slack">/dev/null; then brew cask install slack; fi
if ! open -Ra "Google Drive File Stream">/dev/null; then brew cask install google-drive-file-stream; fi


###
#  ╔╦╗╔═╗╔═╗╦╔═╔╦╗╔═╗╔═╗  ╔═╗╔═╗╔═╗╔═╗
#   ║║║╣ ╚═╗╠╩╗ ║ ║ ║╠═╝  ╠═╣╠═╝╠═╝╚═╗
#  ═╩╝╚═╝╚═╝╩ ╩ ╩ ╚═╝╩    ╩ ╩╩  ╩  ╚═╝
###
echo "Installing essential desktop applications..."
if ! open -Ra "Google Chrome">/dev/null; then brew cask install google-chrome; fi
if ! open -Ra "iTerm">/dev/null; then brew cask install iterm2; fi
if ! open -Ra "Spotify">/dev/null; then brew cask install spotify; fi



###
#  ╔═╗╔═╗╔═╗╦ ╦╦═╗╦╔╦╗╦ ╦  ╔═╗╔═╗╔═╗╔═╗
#  ╚═╗║╣ ║  ║ ║╠╦╝║ ║ ╚╦╝  ╠═╣╠═╝╠═╝╚═╗
#  ╚═╝╚═╝╚═╝╚═╝╩╚═╩ ╩  ╩   ╩ ╩╩  ╩  ╚═╝
###
echo "Installing security applications..."
if ! open -Ra "1Password 6">/dev/null; then brew cask install 1password; fi

sudo defaults write /Library/Preferences/com.apple.alf globalstate -int 1


###
#  ╔╦╗╔═╗╔═╗╦╔═  ╔═╗╔═╗╔═╗╔═╗
#   ║║║ ║║  ╠╩╗  ╠═╣╠═╝╠═╝╚═╗
#  ═╩╝╚═╝╚═╝╩ ╩  ╩ ╩╩  ╩  ╚═╝
###
echo "Sorting out the dock..."


echo "Removing Dock items..."
echo "======================================================================="

dockutil --remove 'Launchpad'
dockutil --remove 'Calendar'
dockutil --remove 'Notes'
dockutil --remove 'Music'
dockutil --remove 'Safari'
dockutil --remove 'FaceTime'
dockutil --remove 'Mail'
dockutil --remove 'Messages'
dockutil --remove 'Maps'
dockutil --remove 'Photos'
dockutil --remove 'Contacts'
dockutil --remove 'Reminders'
dockutil --remove 'TV'
dockutil --remove 'News'
dockutil --remove 'App Store'
dockutil --remove 'System\ Preferenes'

echo "Adding items to the dock..."

dockutil --add /System/Applications/Launchpad.app
dockutil --add /System/Applications/Notes.app
dockutil --add /Applications/Slack.app
dockutil --add /Applications/Safari.app
dockutil --add /Applications/Google\ Chrome.app
dockutil --add /Applications/1Password\ 7.app
dockutil --add /Applications/Spotify.app
dockutil --add /System/Applications/Music.app
dockutil --add /System/Applications/System\ Preferences.app

echo "Dock items set"


###
#  ╔╦╗╔═╗╦ ╦╔═╗╦ ╦ ╔╗ ╔═╗╦═╗
#   ║ ║ ║║ ║║  ╠═╣ ╠╩╗╠═╣╠╦╝
#   ╩ ╚═╝╚═╝╚═╝╩ ╩ ╚═╝╩ ╩╩╚═
###
echo "Setting control strip..."


# Get the Username of the currently logged user
loggedInUser=`/bin/ls -l /dev/console | /usr/bin/awk '{ print $3 }'`
echo $loggedInUser

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



echo "FINISHED SETTING UP"




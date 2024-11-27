# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get update
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb

# Cleanup the .deb file
rm google-chrome-stable_current_amd64.deb

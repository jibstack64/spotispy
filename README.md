# spotispy
[![License: MIT](https://img.shields.io/badge/license-MIT-red.svg)](https://opensource.org/licenses/MIT)

#### spotispy is a small, configurable Spotify playlist sniffer.

### **Required packages:**
- `colorama`
- `toml`
- `spotify`
- `requests`

### How-to:
1. ##### Install requirements
> Assuming you already know a bit about Python: use the pip package manager to install the modules listed under **Required packages**.
1. ##### Setup Spotify application
> Go to https://developer.spotify.com/dashboard and log in using your Spotify account details.
> Once logged in, click **New App** and fill in the required information.
> Copy the application ID and secret to the `config.toml` file.
2. ##### Run!
> Simply run the `spotis.py` script **with** the users you wish to monitor as the following arguments.
> (e.g. `python spotis.py https://open.spotify.com/user/...`)

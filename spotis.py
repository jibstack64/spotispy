# Import required libraries
from colorama import Fore as Colour
import spotify.sync as spotify
import threading
import colorama
import requests
import time
import toml
import sys
import os

# Constant, unchanged variables
CONFIG_PATH = "./config.toml"
_c = toml.load(CONFIG_PATH) # Load config
DELAY, CLIENT_ID, CLIENT_SECRET = tuple(_c["spotify"].values())
TO_CONSOLE, TO_FILE, TO_WEBHOOK = tuple(_c["logger"].values())
USER_URLS = sys.argv[1:]

# Initialise colorama with Windows terminal compatability
if os.name == "nt":
    colorama.init(convert=True)

# Initiate the Spotify client
client = spotify.Client(CLIENT_ID, CLIENT_SECRET)
running = True

# The global dict of user playlist events
# Written to txt file on user interrupt
playlist_events = {}

# Simply logs an event
def log(create: bool, user: spotify.User, pl: spotify.Playlist | str):
    t = f"[{'create' if create else 'remove'}] {'{'+user.id+'}'} {pl if isinstance(pl, str) else pl.url}"
    if TO_CONSOLE:
        print(pretty(t, create))
    if TO_WEBHOOK != "":
        requests.post(TO_WEBHOOK, data={"content": t})

# Prettifies text
def pretty(text: str, success: bool = True) -> str:
    formatting = {
        "{}": Colour.LIGHTBLUE_EX,
        "[]": Colour.LIGHTGREEN_EX if success else Colour.LIGHTRED_EX
    }
    # Loop through each character in the text and apply formatting
    char_set = [(k[0], k[1],) for k in formatting.keys()]
    in_bracket = 0
    char_pos = 0
    new_text = ""
    for c in text:
        if in_bracket == 0:
            for s in char_set:
                if c == s[0] and s[1] in text:
                    new_text += Colour.LIGHTBLACK_EX
                    new_text += c
                    new_text += formatting[s[0]+s[1]]
                    in_bracket = s
            if in_bracket == 0:
                new_text += c
        else:
            if c == in_bracket[1]:
                new_text += Colour.LIGHTBLACK_EX
                new_text += c
                new_text += Colour.RESET
                in_bracket = 0
            else:
                new_text += c
        char_pos += 1
    return new_text

# Listens for new playlist creation or deletion events on the provided Spotify user id
def listen(u_id: str):
    user = client.get_user(u_id)
    playlist_events[user] = []
    playlists = [p.id for p in user.get_all_playlists()]
    # Constantly listen for new playlists
    while running:
        new = user.get_all_playlists()
        # If any playlists new
        for pl in new:
            if pl.id not in playlists:
                # PLAYLIST ADD
                playlists.append(pl.id)
                playlist_events[user].append("A|"+pl.url)
                log(True, user, pl)
        # If a playlist is removed
        for pl in playlists:
            pl = client.http.get_playlist(pl)
            if pl["id"] not in [n.id for n in new]:
                # PLAYLIST REMOVE
                playlists.remove(pl["id"])
                playlist_events[user].append("R|"+pl["external_urls"]["spotify"])
                log(False, user, pl["external_urls"]["spotify"])
    time.sleep(DELAY)    

try:
    for u in USER_URLS:
        threading.Thread(target=listen, args=(u.split("user/")[1].split("?")[0],)).start()
    
    # Main run loop; locks thread
    while running:
        continue

# When the user wants outsies
except KeyboardInterrupt:
    if TO_FILE != "":
        f = open(TO_FILE, "a")
        s = ""
        for user, events in playlist_events.items():
            for ev in events:
                s += f"\n{user.display_name} | {user.id} : {'ADD' if ev.startswith('A') else 'REMOVE'} {ev[2:]}"
        f.write(s)
finally:
    running = False
    client.close()

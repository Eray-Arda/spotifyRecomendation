import spotipy
import openai
from spotipy.oauth2 import SpotifyOAuth

API_KEY = ""
openai.api_key = API_KEY

client_id = ""
client_secret = ""
redirect_uri = 'http://localhost:8888/callback'
scope = ' '.join([
    'user-library-read',
    'user-library-modify',
    'playlist-read-private',
    'playlist-read-collaborative',
    'playlist-modify-public',
    'playlist-modify-private',
    'user-read-recently-played',
    'user-top-read',
    'user-follow-read',
    'user-follow-modify',
    'user-read-playback-state',
    'user-modify-playback-state',
    'user-read-currently-playing',
    'app-remote-control',
    'streaming',
    'user-read-email',
    'user-read-private'
])

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))


def get_playlist_ID(playlists): #Gets playlist ID
    playlistsID = [] #List of playlists IDs
    playlists = playlists["items"]

    for item in playlists:
        playlistsID.append(item["id"])
    
    return playlistsID


def get_track_from_playlist(playlistID): #Gets all the tracks from a single playlist
    tracks = []
    results = spotify.playlist_tracks(playlistID, limit = 100)
    tracks.extend(results["items"])
    
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results["items"])
    
    return tracks

def askAI(tracks, no_of_suggestion): #Asks gpt-4o-mini for song recomendations
    prompt = f"A person likes these songs:\n{tracks}\nCan you suggest {no_of_suggestion} more song(s) that this person will like? Make sure there aren't duplicates in your suggestions and don't suggest songs already on this list. Give only song suggestions no other explanation. Give only the songs' name not their artists. Seperate the songs by a dash sign."
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages= [
            {"role": "user", "content": prompt},
            ]
    )
    return response.choices[0].message.content.strip("\n")

def get_track_name_and_artist(tracks): #Gets the name of the song and the artists
    track_artist_name = ""
    for track in tracks:
        track_name = track["track"]["name"]
        artist_name = ""

        for artist in track["track"]["artists"]:
            artist_name += (artist["name"])
            artist_name = ""
        track_artist_name = track_artist_name + track_name + "" + artist_name + "\n"

    return track_artist_name

def get_track_from_playlist(playlistID, limit):
    tracks = []
    results = spotify.playlist_tracks(playlistID, limit = limit)
    tracks.extend(results["items"])
    return tracks

def get_track_info(track):
    track_info = []
    track_info.append(spotify.search(q= track, type = "track", limit=1))
    only_track = track_info[0]
    return only_track

def askSpotify(seed_tracks, limit): #Returns spotify recommendations
    return spotify.recommendations(seed_tracks = seed_tracks, limit = limit)["tracks"]

def add_track_to_playlist(playlist_id, track_ids): #Adds a list of songs to a playlist
    spotify.playlist_add_items(playlist_id= playlist_id, items = track_ids)

def song_liked(song_id):
    liked_songs_ids.append(song_id)

liked_songs_ids = []

current_User = spotify.current_user() #Gets user profile
curr_ID = current_User["id"] #Gets users ID from profile
playlists = spotify.user_playlists(curr_ID, limit = 10) #Gets users playlists
playlistIDs = get_playlist_ID(playlists) #Gets ids of all the playlists passed

playlistID = playlistIDs[0] #Selecting which playlist to use


tracks_in_playlist = get_track_from_playlist(playlistID, 5) #Gets playlists last added 5 songs
track_name_artist = get_track_name_and_artist(tracks_in_playlist) #Gets the tracks names
#response = askAI(track_name_artist, 1) #Ask AI to recommend songs
#print(response)
#single_tracks = response.split("-")
#for track in single_tracks:
#    track_info = get_track_info(track)
#    print(track_info["tracks"]["items"][0]["preview_url"])

track_ids = []
for track in tracks_in_playlist:
    track_ids.append(track["track"]["id"])

suggested_tracks = askSpotify(track_ids, 10)

for track in suggested_tracks:
    track_name = track['name']
    artist_names = ', '.join([artist['name'] for artist in track['artists']])
    preview_url = track.get('preview_url', 'No preview available')
    album_image_url = track['album']['images'][0]['url'] if track['album']['images'] else 'No image available'
            
    print(f"Track Name: {track_name}")
    print(f"Artist(s): {artist_names}")
    print(f"Preview URL: {preview_url}")
    print(f"Album Image URL: {album_image_url}\n")


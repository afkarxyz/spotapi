from flask import Flask, jsonify
from spotapi import PublicTrack, PublicAlbum, PublicPlaylist
from cachetools import cached, TTLCache
import re

app = Flask(__name__)

# Create a cache with a maximum of 100 items and a TTL of 1 hour (3600 seconds)
metadata_cache = TTLCache(maxsize=100, ttl=3600)

def extract_spotify_id(url):
    """
    Extract Spotify ID from full Spotify URL or just ID
    """
    patterns = [
        r'spotify\.com/track/([a-zA-Z0-9]{22})',
        r'spotify\.com/album/([a-zA-Z0-9]{22})',
        r'spotify\.com/playlist/([a-zA-Z0-9]{22})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return url

@app.route('/track/<path:track_input>')
@cached(metadata_cache)
def get_track_metadata(track_input):
    """
    Retrieve raw track metadata
    Support both direct ID and full Spotify URL
    """
    try:
        track_id = extract_spotify_id(track_input)
        track = PublicTrack(track_id)
        return jsonify(track.get_track_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/album/<path:album_input>')
@cached(metadata_cache)
def get_album_metadata(album_input):
    """
    Retrieve raw album metadata
    Support both direct ID and full Spotify URL
    """
    try:
        album_id = extract_spotify_id(album_input)
        album = PublicAlbum(album_id)
        return jsonify(album.get_album_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/playlist/<path:playlist_input>')
@cached(metadata_cache)
def get_playlist_metadata(playlist_input):
    """
    Retrieve raw playlist metadata
    Support both direct ID and full Spotify URL
    """
    try:
        playlist_id = extract_spotify_id(playlist_input)
        playlist = PublicPlaylist(playlist_id)
        return jsonify(playlist.get_playlist_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/<path:url>')
def handle_full_url(url):
    """
    Handle full Spotify URLs and redirect to appropriate endpoint
    """
    if 'track' in url:
        return get_track_metadata(url)
    elif 'album' in url:
        return get_album_metadata(url)
    elif 'playlist' in url:
        return get_playlist_metadata(url)
    else:
        return jsonify({'error': 'Invalid Spotify URL'}), 400

@app.errorhandler(404)
def not_found(error):
    """
    Custom 404 error handler
    """
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

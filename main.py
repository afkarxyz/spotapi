from flask import Flask, jsonify, make_response
from spotapi import PublicTrack, PublicAlbum, PublicPlaylist
from cachetools import cached, TTLCache
import re

app = Flask(__name__)

# Create a cache with a maximum of 100 items and a TTL of 1 hour (3600 seconds)
metadata_cache = TTLCache(maxsize=100, ttl=3600)

def get_usage_html():
    """
    Returns HTML template for API usage documentation
    """
    return """
<!DOCTYPE html>
<html>
<head>
    <title>API Endpoints Usage</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            color: #333;
        }
        h1 {
            color: #1DB954;
            border-bottom: 2px solid #1DB954;
            padding-bottom: 10px;
        }
        h2 {
            color: #444;
            margin-top: 30px;
        }
        code {
            background: #f5f5f5;
            padding: 3px 6px;
            border-radius: 3px;
            border: 1px solid #ddd;
            font-family: Monaco, "Courier New", monospace;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>API Endpoints Usage</h1>

    <h2>Get Track Metadata</h2>
    <code>/track/{track_id}</code><br><br>
    <code>/https://open.spotify.com/track/{track_id}</code>

    <h2>Get Album Metadata</h2>
    <code>/album/{album_id}</code><br><br>
    <code>/album/{album_id}?limit=X&offset=Y</code><br><br>
    <code>/https://open.spotify.com/album/{album_id}</code>

    <h2>Get Playlist Metadata</h2>
    <code>/playlist/{playlist_id}</code><br><br>
    <code>/playlist/{playlist_id}?limit=X&offset=Y</code><br><br>
    <code>/https://open.spotify.com/playlist/{playlist_id}</code>
</body>
</html>
"""

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
    Retrieve raw album metadata with pagination support
    Support both direct ID and full Spotify URL
    Supports optional limit and offset parameters
    """
    try:
        album_id = extract_spotify_id(album_input)
        album = PublicAlbum(album_id)
        
        # Get query parameters with defaults
        limit = int(app.config.get('limit', 50))
        offset = int(app.config.get('offset', 0))
        locale = app.config.get('locale', 'en')
        
        # If requesting all tracks, use pagination
        if limit == -1:
            all_tracks = []
            for tracks_chunk in album.paginate_album_tracks(locale=locale):
                all_tracks.extend(tracks_chunk['items'])
            
            # Replace tracks with compiled list
            album_info = album.get_album_info(limit=50, locale=locale)
            album_info['data']['albumUnion']['tracks']['items'] = all_tracks
            album_info['data']['albumUnion']['tracks']['totalCount'] = len(all_tracks)
            
            return jsonify(album_info)
        
        # Standard retrieval with limit and offset
        return jsonify(album.get_album_info(limit=limit, offset=offset, locale=locale))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/playlist/<path:playlist_input>')
@cached(metadata_cache)
def get_playlist_metadata(playlist_input):
    """
    Retrieve raw playlist metadata with pagination support
    Support both direct ID and full Spotify URL
    Supports optional limit and offset parameters
    """
    try:
        playlist_id = extract_spotify_id(playlist_input)
        playlist = PublicPlaylist(playlist_id)
        
        # Get query parameters with defaults
        limit = int(app.config.get('limit', 343))
        offset = int(app.config.get('offset', 0))
        
        # If requesting all tracks, use pagination
        if limit == -1:
            all_tracks = []
            for tracks_chunk in playlist.paginate_playlist():
                all_tracks.extend(tracks_chunk['items'])
            
            # Replace tracks with compiled list
            playlist_info = playlist.get_playlist_info(limit=343)
            playlist_info['data']['playlistV2']['content']['items'] = all_tracks
            playlist_info['data']['playlistV2']['content']['totalCount'] = len(all_tracks)
            
            return jsonify(playlist_info)
        
        # Standard retrieval with limit and offset
        return jsonify(playlist.get_playlist_info(limit=limit, offset=offset))
    
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
        response = make_response(get_usage_html(), 400)
        response.headers['Content-Type'] = 'text/html'
        return response

@app.errorhandler(404)
def not_found(error):
    """
    Custom 404 error handler with API usage information
    """
    response = make_response(get_usage_html(), 404)
    response.headers['Content-Type'] = 'text/html'
    return response

if __name__ == '__main__':
    app.run(debug=True)

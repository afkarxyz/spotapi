from flask import Flask, jsonify
from spotapi import PublicTrack, PublicAlbum, PublicPlaylist
from cachetools import cached, TTLCache

app = Flask(__name__)

# Create a cache with a maximum of 100 items and a TTL of 1 hour (3600 seconds)
metadata_cache = TTLCache(maxsize=100, ttl=3600)

@app.route('/track/<track_id>')
@cached(metadata_cache)
def get_track_metadata(track_id):
    """
    Retrieve raw track metadata
    """
    try:
        track = PublicTrack(track_id)
        return jsonify(track.get_track_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/album/<album_id>')
@cached(metadata_cache)
def get_album_metadata(album_id):
    """
    Retrieve raw album metadata
    """
    try:
        album = PublicAlbum(album_id)
        return jsonify(album.get_album_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/playlist/<playlist_id>')
@cached(metadata_cache)
def get_playlist_metadata(playlist_id):
    """
    Retrieve raw playlist metadata
    """
    try:
        playlist = PublicPlaylist(playlist_id)
        return jsonify(playlist.get_playlist_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.errorhandler(404)
def not_found(error):
    """
    Custom 404 error handler
    """
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

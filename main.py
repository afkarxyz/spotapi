from flask import Flask, jsonify
from spotapi import PublicTrack, PublicAlbum, PublicPlaylist
from cachetools import TTLCache, cached
from functools import wraps

# Create global cache instances with TTL (Time-To-Live)
track_cache = TTLCache(maxsize=100, ttl=3600)  # Cache tracks for 1 hour
album_cache = TTLCache(maxsize=100, ttl=3600)  # Cache albums for 1 hour
playlist_cache = TTLCache(maxsize=100, ttl=3600)  # Cache playlists for 1 hour

app = Flask(__name__)

def cache_with_ttl(cache):
    """
    Decorator to apply caching with TTL to methods
    
    :param cache: Cache instance to use
    :return: Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(id):
            # Check if the result is in cache
            if id in cache:
                return cache[id]
            
            # If not in cache, call the original function
            result = func(id)
            
            # Store the result in cache
            cache[id] = result
            
            return result
        return wrapper
    return decorator

@app.route('/track/<track_id>', methods=['GET'])
@cache_with_ttl(track_cache)
def get_track_info(track_id: str):
    """
    Retrieve track information by Spotify track ID
    
    :param track_id: Spotify track ID
    :return: JSON response with track information
    """
    try:
        # Create PublicTrack instance
        track = PublicTrack(track_id)
        
        # Get track information
        track_info = track.get_track_info()
        
        return jsonify(track_info)
    except ValueError as ve:
        # Handle invalid track ID
        return jsonify({"error": "Bad Request", "message": str(ve)}), 400
    except Exception as e:
        # Handle other potential errors
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/album/<album_id>', methods=['GET'])
@cache_with_ttl(album_cache)
def get_album_info(album_id: str):
    """
    Retrieve album information by Spotify album ID
    
    :param album_id: Spotify album ID
    :return: JSON response with album information
    """
    try:
        # Create PublicAlbum instance
        album = PublicAlbum(album_id)
        
        # Get album information
        album_info = album.get_album_info()
        
        return jsonify(album_info)
    except ValueError as ve:
        # Handle invalid album ID
        return jsonify({"error": "Bad Request", "message": str(ve)}), 400
    except Exception as e:
        # Handle other potential errors
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/playlist/<playlist_id>', methods=['GET'])
@cache_with_ttl(playlist_cache)
def get_playlist_info(playlist_id: str):
    """
    Retrieve playlist information by Spotify playlist ID
    
    :param playlist_id: Spotify playlist ID
    :return: JSON response with playlist information
    """
    try:
        # Create PublicPlaylist instance
        playlist = PublicPlaylist(playlist_id)
        
        # Get playlist information
        playlist_info = playlist.get_playlist_info()
        
        return jsonify(playlist_info)
    except ValueError as ve:
        # Handle invalid playlist ID
        return jsonify({"error": "Bad Request", "message": str(ve)}), 400
    except Exception as e:
        # Handle other potential errors
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_cache():
    """
    Clear all caches
    
    :return: JSON response indicating successful cache clearing
    """
    track_cache.clear()
    album_cache.clear()
    playlist_cache.clear()
    
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
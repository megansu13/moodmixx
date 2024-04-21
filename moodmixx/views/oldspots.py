import json
import time
import flask
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, Flask, jsonify, request, redirect, g, render_template, session, url_for
import requests
from urllib.parse import quote
from moodmixx import app

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.

spots = Blueprint("oldspots", __name__)

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.config['SESSION_PERMANENT'] = False
app.secret_key = 'sdfjios#*749872$&%^*A80'
TOKEN_INFO = 'token_info'

@spots.route('/home')
def home():
    return jsonify({"status": "success", "message": "User is home"}), 200

@spots.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('spots.home'))

@spots.route('/login')
def login():
	sp_oauth = create_spotify_oauth()
	auth_url = sp_oauth.get_authorize_url()
	return redirect(auth_url)

@spots.route('/redirect')
def redirect_page():
	sp_oauth = create_spotify_oauth()
	session.clear() 
	code = request.args.get('code')
	token_info = sp_oauth.get_access_token(code)
	session[TOKEN_INFO] = token_info
	return redirect(url_for("spots.getDaylist", _external=True))

@spots.route('/tracks')
def tracks():
	token_info = get_token()
	sp = spotipy.Spotify(auth=token_info['access_token'])
	tracks = sp.current_user_saved_tracks()["items"]
	for track in tracks:
		print(track["track"]["name"])
	return "check the terminal"

@spots.route('/addTrack', methods=["POST"])
def add_track_to_library():
	try:
		track_id = request.json.get('trackId')
		if not track_id:
			return jsonify({'status': 'error', 'message': 'No track_id provided'}), 400
		sp = spotipy.Spotify(auth=get_token()['access_token'])
		sp.current_user_saved_tracks_add(tracks=[track_id])
		return jsonify({'status': 'success', 'message': 'Track added'}), 200
	except spotipy.exceptions.SpotifyException as e:
		print(f"Spotify API error: {e}")
		return jsonify({'status': 'error', 'message': str(e), 'code': e.http_status}), e.http_status
	except Exception as e:
		print(f"Unexpected error: {e}")
		return jsonify({'status': 'error', 'message': str(e)}), 500

@spots.route('/check')
def check_login():
    try:
        token_info = get_token()  # Assuming this function validates the token and raises an exception if invalid
        # If get_token() is successful, it means the user is logged in
        return jsonify({"status": "success", "message": "User is logged in."}), 200
    except Exception as e:
        # Catch-all for any other unexpected exceptions
        print(f"Unexpected error during login check: {e}")
        return jsonify({"status": "error", "message": "Invalid token. Please log in again."}), 401
	# except:
	# 	print("User not logged in")
	# 	return redirect(url_for('spots.login', _external=False))

@spots.route('/getDaylist')
def getDaylist():
	token_info = get_token()
	sp = spotipy.Spotify(auth=token_info['access_token'])
	daylist_playlist_id = 0
	saved_weekly_playlist_id = 0
	# current_playlists = sp.category_playlists("mood", limit=50)["playlists"]["items"]
	current_playlists = sp.current_user_playlists()["items"]

	for playlist in current_playlists:
		if "StarBoy" in playlist['name']:
			daylist_playlist_id = playlist['id']
		if(playlist['name'] == 'Saved Weekly'):
			saved_weekly_playlist_id = playlist['id']

	if not daylist_playlist_id:
		return 'Daylist not found'

	daylist_playlist = sp.playlist_items(daylist_playlist_id)
	song_info = []
	for song in daylist_playlist['items']:
		song_id = song['track']['id']
		# Spotify api access to specific song_id
		song_all_info = sp.track(song_id)
		song_info.append(
			{				
				"album_name": song_all_info['album']['name'],
				"album_cover": song_all_info['album']['images'][0]['url'],
				"artist_names": song_all_info['artists'][0]['name'],
				"song_name": song_all_info['name'],
				"preview_url": song_all_info['preview_url'],
				"track_id": song_all_info['id']
			}
		)

	context = {
		"song_info": song_info
	}
	return flask.jsonify(**context), 200

def get_token():
	token_info = session.get(TOKEN_INFO, None)
	if not token_info:
		raise "exception"
	now = int(time.time())
	is_expired = token_info['expires_at'] - now < 60
	if(is_expired):
		spotify_oauth = create_spotify_oauth()
		token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
		session[TOKEN_INFO] = token_info
	return token_info

def create_spotify_oauth():
	return SpotifyOAuth(
		client_id = "913923a1251d4f90b46aedfee11d2f6b",
		client_secret = "10869cb3995f4e75afa8d8a12cc40106",
		redirect_uri = url_for('spots.redirect_page', _external = True),
		scope = 'user-library-read user-library-modify playlist-modify-public playlist-modify-private'
	)
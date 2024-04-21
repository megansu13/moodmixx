import json
import logging
import random
import string
import time
import flask
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Blueprint, Flask, jsonify, request, redirect, g, render_template, session, url_for, make_response, send_from_directory
import requests
from urllib.parse import quote
from moodmixx import app
from flask_cors import CORS, cross_origin

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.

spots = Blueprint("spots", __name__)
# redirect_uri = "http://localhost:8080/redirect"
redirect_uri = "https://moodmixx-app-30a3f646f185.herokuapp.com/redirect"
app.secret_key = 'sdfjios#*749872$&%^*A80'

@spots.route('/')
@spots.route('/home')
@cross_origin()
def home():
    return jsonify({"status": "success", "message": "User is home"}), 200

# @spots.route('/')
# @cross_origin()
# def serve():
# 	return send_from_directory(app.static_folder, 'index.html')

@spots.route('/authorize')
@cross_origin()
def authorize():
	client_id = app.config['CLIENT_ID']
	scope = app.config['SCOPE']
	# state key used to protect against cross-site forgery attacks
	state_key = createStateKey(15)
	session['state_key'] = state_key
	# redirect user to Spotify authorization page
	authorize_url = 'https://accounts.spotify.com/en/authorize?'
	parameters = 'response_type=code&client_id=' + client_id + '&redirect_uri=' + redirect_uri + '&scope=' + scope + '&state=' + state_key
	response = make_response(redirect(authorize_url + parameters))

	return response

@spots.route('/redirect')
@cross_origin()
def redirect_page():
	# make sure the response came from Spotify
	if request.args.get('state') != session['state_key']:
		return render_template('index.html', error='State failed.')
	if request.args.get('error'):
		return render_template('index.html', error='Spotify error.')
	else:
		code = request.args.get('code')
		session.pop('state_key', None)

		# get access token to make requests on behalf of the user

		payload = getToken(code)
		if payload != None:
			session['refresh_token'] = payload[1]
			session['token'] = payload[0]
			session['token_expiration'] = time.time() + payload[2]
		else:
			return "Failure"
	current_user = getUserInformation(session)
	session['user_id'] = current_user['id']
	logging.info('new user:' + session['user_id'])

	# return redirect("http://localhost:3000/content")
	return redirect("/content")

@spots.route('/playlistTracks', methods = ['GET'])
@cross_origin()
def playlistTracks():
	# make sure application is authorized for user 
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/tracks'
		return redirect('/authorize')

	# collect user information
	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']

	playlist_id = "37i9dQZF1EP6YuccBxUcC1"
	track_ids = getPlaylistTracks(session, playlist_id)

	if track_ids == None:
		return "No Tracks"
	return track_ids

@spots.route('/addTrack', methods=["PUT"])
@cross_origin()
def addSong():
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/tracks'
		return redirect('/authorize')

	# collect user information
	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']
	track_id = request.json.get('trackId')
	addTracks(session, track_id)
	return jsonify({'status': 'success', 'message': 'Track added'}), 200

@spots.route('/removeTrack')
@cross_origin()
def removeSong():
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/tracks'
		return redirect('/authorize')
	# collect user information
	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']
	track_id = request.json.get('trackId')
	removeTracks(session, track_id)
	return jsonify({'status': 'success', 'message': 'Track added'}), 200

def refreshToken(refresh_token):
	token_url = 'https://accounts.spotify.com/api/token'
	authorization = app.config['AUTHORIZATION']

	headers = {'Authorization': authorization, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	body = {'refresh_token': refresh_token, 'grant_type': 'refresh_token'}
	post_response = requests.post(token_url, headers=headers, data=body)

	# 200 code indicates access token was properly granted
	if post_response.status_code == 200:
		return post_response.json()['access_token'], post_response.json()['expires_in']
	else:
		logging.error('refreshToken:' + str(post_response.status_code))
		return None
	
def getToken(code):
	token_url = 'https://accounts.spotify.com/api/token'
	authorization = app.config['AUTHORIZATION']

	headers = {'Authorization': authorization, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	body = {'code': code, 'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'}
	post_response = requests.post(token_url, headers=headers, data=body)

	# 200 code indicates access token was properly granted
	if post_response.status_code == 200:
		json = post_response.json()
		return json['access_token'], json['refresh_token'], json['expires_in']
	else:
		logging.error('getToken:' + str(post_response.status_code))
		return None

def createStateKey(size):
	#https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))

def checkTokenStatus(session):
	if time.time() > session['token_expiration']:
		payload = refreshToken(session['refresh_token'])

		if payload != None:
			session['token'] = payload[0]
			session['token_expiration'] = time.time() + payload[1]
		else:
			logging.error('checkTokenStatus')
			return None
	return "Success"

def makeGetRequest(session, url, params={}):
	headers = {"Authorization": "Bearer {}".format(session['token'])}
	response = requests.get(url, headers=headers, params=params)

	# 200 code indicates request was successful
	if response.status_code == 200:
		return response.json()

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and checkTokenStatus(session) != None:
		return makeGetRequest(session, url, params)
	else:
		logging.error('makeGetRequest:' + str(response.status_code))
		return None

def makePutRequest(session, url, params={}, data={}):
	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.put(url, headers=headers, params=params, data=data)

	# if request succeeds or specific errors occured, status code is returned
	if response.status_code == 204 or response.status_code == 403 or response.status_code == 404 or response.status_code == 500:
		return response.status_code

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and checkTokenStatus(session) != None:
		return makePutRequest(session, url, data)
	else:
		logging.error('makePutRequest:' + str(response.status_code))
		return None

def makePostRequest(session, url, data):
	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	response = requests.post(url, headers=headers, data=data)

	# both 201 and 204 indicate success, however only 201 responses have body information
	if response.status_code == 201:
		return response.json()
	if response.status_code == 204:
		return response

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and checkTokenStatus(session) != None:
		return makePostRequest(session, url, data)
	elif response.status_code == 403 or response.status_code == 404:
		return response.status_code
	else:
		logging.error('makePostRequest:' + str(response.status_code))
		return None

def makeDeleteRequest(session, url, data):
	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	response = requests.delete(url, headers=headers, data=data)

	# 200 code indicates request was successful
	if response.status_code == 200:
		return response.json()

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and checkTokenStatus(session) != None:
		return makeDeleteRequest(session, url, data)
	else:
		logging.error('makeDeleteRequest:' + str(response.status_code))
		return None
	
def getUserInformation(session):
	url = 'https://api.spotify.com/v1/me'
	payload = makeGetRequest(session, url)
	if payload == None:
		logging.error("this did not work")
		return None
	return payload

def getPlaylistTracks(session, playlist_id, limit=50):
	url = 'https://api.spotify.com/v1/playlists/' + playlist_id
	offset = 0
	song_info = []
	params = {'limit': limit, 'offset': offset}
	payload = makeGetRequest(session, url, params)

	if payload == None:
		return None
	
	for song_all_info in payload['tracks']['items']:
		song_info.append( 
			{				
				"album_name": song_all_info['track']['album']['name'],
				"album_cover": song_all_info['track']['album']['images'][0]['url'],
				"artist_names": song_all_info['track']['artists'][0]['name'],
				"song_name": song_all_info['track']['name'],
				"preview_url": song_all_info['track']['preview_url'],
				"track_id": song_all_info['track']['id']
			}
		)
	context = {
		"song_info": song_info
	}
	return flask.jsonify(**context), 200

def getCategoryPlaylists(session, limit=20):
	url = 'https://api.spotify.com/v1/browse/categories/mood/playlists'
	offset = 0
	playlists = []

	# iterate through all playlists of a user (Spotify limits amount returned with one call)
	total = 1
	while total > offset:
		params = {'limit': limit, 'offset': offset}
		payload = makeGetRequest(session, url, params)

		if payload == None:
			return None
		
		for item in payload['playlists']['items']:
			playlists.append(
				{
					"playlist_name":item['name'],
					"playlist_uri": item['uri'], 
					"playlist_cover": item['images'][0]['url']
				}
			)

		total = payload['playlists']['total']
		offset += limit
	context = {
		"playlists": playlists
	}
	return flask.jsonify(**context), 200

def removeTracks(session, track_id):
	url='https://api.spotify.com/v1/me/tracks?ids=' + track_id
	data = "{\"ids\": [" + track_id + "]}"
	makeDeleteRequest(session, url, data)

def addTracks(session, track_id):
	url='https://api.spotify.com/v1/me/tracks?ids=' + track_id
	data = "{\"ids\": [" + track_id + "]}"
	makePutRequest(session, url, data)
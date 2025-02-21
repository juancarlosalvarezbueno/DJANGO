from rest_framework import generics
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view
import json
import random
import string
import requests
import webbrowser
from .models import Usuario, Song
from django.http import HttpResponseRedirect

CLIENT_ID = "82c38d08d2f548da9a5388093b863b9d"
CLIENT_SECRET = "b2c5b2947e784c799ec2f28345680910"
REDIRECT_URI = "http://localhost:8000/callback"
scope = 'user-top-read'
json_users= "users.json"
token_file="token.json"

def random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_refresh_token():
    
    try:
        with open(token_file, "r") as file:
            token_info = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    refresh_token = token_info.get("refresh_token")
    if not refresh_token:
        return None 

    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        new_token_info = response.json()

        
        new_token_info["refresh_token"] = refresh_token  
        with open(token_file, "w") as file:
            json.dump(new_token_info, file, indent=4)

        return new_token_info["access_token"]

    return None


@api_view(["GET"])
def login(request):
    state = random_string(16)
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={REDIRECT_URI}&state={state}"
    return webbrowser.open(url=auth_url)
    
    

def callback(request):
    code = request.GET.get('code')
    token_info = token_request(code)
    if token_info:
        with open('token.json', 'w') as file:
            json.dump(token_info, file, indent=4)
        return JsonResponse({"message": "Authorization successful", "access_token": token_info})
    else:
        return JsonResponse({"message": "Failed to get access token"}, status=400)

def token_request(code):
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_top_artists(request):
    try:
        with open('token.json', 'r') as file:
            token_info = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return JsonResponse({"error": f"Error reading token: {str(e)}"}, status=400)

    #if not token_info:
        #return JsonResponse({"error": "Access token not available"}, status=400)

    access_token = get_refresh_token() or token_info.get("access_token")

    if not access_token:
        return JsonResponse({"error": "Access token not available"}, status=400)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    params = {'time_range': 'medium_term', 'limit': 10}
    response = requests.get("https://api.spotify.com/v1/me/top/artists", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        artist_names = [track['name'] for track in data['items']]
        return JsonResponse({"favourite_artists": artist_names})
    else:
        return JsonResponse({"error": f"Error: {response.status_code}, {response.text}"}, status=400)

    
def get_top_songs(request):
    try:
        with open('token.json', 'r') as file:
            token_info = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return JsonResponse({"error": f"Error reading token: {str(e)}"}, status=400)

    access_token = get_refresh_token() or token_info.get("access_token")

    if not access_token:
        return JsonResponse({"error": "Access token not available"}, status=400)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    access_token = token_info.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {'time_range': 'long_term', 'limit': 10}
    response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        song_names = [song['name'] for song in data['items']]
        return JsonResponse({"favourite_songs": song_names})
    else:

        return JsonResponse({"error": f"Error: {response.status_code}, {response.text}"}, status=400)

#@csrf_exempt  
@api_view(["POST"])  
def create_user(request:Usuario):
    print(request.body)
    try:
      
        with open(json_users, "r") as file:
            saved_users = json.load(file)
    except FileNotFoundError:
        saved_users = []

# Obtenengo los datos del usuario
    user_data = request.data  #request.data para obt el cuerpo de la sol en formato JSON

# Compruebo que user esté en los datos
    if "user" not in user_data:
        return JsonResponse({"error": "'user' field is required"}, status=400)

# compruebo si el usuario ya existe
    if any(u["user"] == user_data["user"] for u in saved_users):
        return JsonResponse({"error": "This user already exists"}, status=400)

#  Creo el nuevo usuario con una array vacia para las canciones
    new_user = {
        "user": user_data["user"],
        "songs": user_data["songs"]
    }

    saved_users.append(new_user)

#Guardo los usuarios actualizados en el archivo JSON
    with open(json_users, "w") as file:
        json.dump(saved_users, file, indent=4)

# Resp con el mensaje de éxito y los datos del nuevo usuario
    return JsonResponse({"message": "User created", "user": new_user}, status=201)

        
    #     try:
    #         
    #         data = json.loads(request.body)
    #         user = data.get('user')
    #         songs = data.get('songs', [])

    #         if not user:
    #             return JsonResponse({'error': 'User is required'}, status=400)

    #         

    #         return JsonResponse({'message': 'User created successfully', 'user': user, 'songs': songs}, status=201)
    #     except json.JSONDecodeError:
    #         return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    # else:
    #     return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

#@csrf_exempt
@api_view(["GET"])
def see_users(request):
    try:
        with open('users.json', 'r') as file:
            saved_users = json.load(file)
        return JsonResponse({"users": saved_users})
    except FileNotFoundError:
        return JsonResponse({"error": "Users not found"}, status=404)

@api_view(["GET"])
def see_user(request, user):
    try:
     
        with open('users.json', 'r') as file:
            users = json.load(file)

        user_data = next((u for u in users if u['user'] == user), None)

        if user_data is not None:
            return JsonResponse({'user': user_data}, status=200)
        else:
            return JsonResponse({'error': 'User not found'}, status=404)
    
    except FileNotFoundError:
        return JsonResponse({'error': 'No users data available'}, status=500)

@api_view(["PUT"])
def modify_preferences(request, user ):
    try:
        with open('users.json', 'r') as file:
            saved_users = json.load(file)

        user_data = next((u for u in saved_users if u["user"] == user), None)
        if not user_data:
            return JsonResponse({"error": "User not found"}, status=404)

        
        new_songs = json.loads(request.body).get('songs', [])
        if new_songs:
            user_data["songs"].extend(new_songs)

        with open('users.json', 'w') as file:
            json.dump(saved_users, file, indent=4)

        return JsonResponse({"message": "User preferences updated", "user": user_data})

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    
 
@api_view(["DELETE"])
def delete_user(request,user):
    try:
        with open('users.json', 'r') as file:
            saved_users = json.load(file)

        user_to_remove = next((u for u in saved_users if u["user"] == user), None)
        if not user_to_remove:
            return JsonResponse({"error": "User not found"}, status=404)

        saved_users = [u for u in saved_users if u["user"] != user]

        with open('users.json', 'w') as file:
            json.dump(saved_users, file, indent=4)

        return JsonResponse({"message": f"User '{user}' deleted"})

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


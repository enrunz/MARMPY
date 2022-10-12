import streamlit as st
import pandas as pd
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import requests
import json 
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize

import plotly.express as pex
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering, KMeans, DBSCAN
from sklearn.neighbors import NearestNeighbors
from kneed import KneeLocator
from sklearn.cluster import FeatureAgglomeration

import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot

from statsmodels.stats.weightstats import ztest as ztest

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import plotly.graph_objects as go
import plotly.offline as pyo
import plotly
from plotly.offline import iplot, init_notebook_mode
init_notebook_mode(connected = True)

import warnings
warnings.filterwarnings("ignore")
from PIL import Image


video_file = open('MARMPY_L.mp4', 'rb')
video_bytes = video_file.read()

st.video(video_bytes)


st.title('MARMPY')

CLIENT_ID = "e83d3836d10b4d06a00845db78de3dfb"
CLIENT_SECRET = "6aab53d5a2074b6d9552fb767cdf142c"

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=auth_manager)


def playlisttodf(x):
    playlist=pd.DataFrame(spotify.playlist_items(x))
    flatten_1=pd.json_normalize(playlist['items'])
    songlist=[]
    for i in flatten_1['track.external_urls.spotify']:
        songlist.append(spotify.audio_features(i))
    df=pd.DataFrame(songlist)
    flatten_2=pd.json_normalize(df[0])
    final_playlist=pd.concat(((flatten_1['track.name']),flatten_2),axis=1)
    final_playlist['track_number_inlist']=final_playlist.index+1
    final_playlist['minutestamp']=(final_playlist['duration_ms'].cumsum())/60000
    y=spotify.playlist(x)['name']
    final_playlist['original_playlist']= y
    return final_playlist

def createpca(x):
    sfeat=['danceability', 'energy', 'loudness',
       'speechiness', 'acousticness', 'instrumentalness', 'liveness',
       'valence', 'tempo']
    scaler = StandardScaler()
    scaler.fit(x[sfeat])
    x_sca = pd.DataFrame(
    scaler.transform(x[sfeat]), columns=scaler.feature_names_in_)
    x_pca = PCA(n_components= 2)
    x_pca.fit(x_sca)
    x_transformed= pd.DataFrame(x_pca.transform(x_sca),columns=["PC" + str(i) for i in range(x_pca.n_components_)])
    playlist_with_pca=pd.concat((x,x_transformed),axis=1)
    return playlist_with_pca

def pcatopool(x,y):
    sfeat=['danceability', 'energy', 'loudness',
       'speechiness', 'acousticness', 'instrumentalness', 'liveness',
       'valence', 'tempo']
    scaler = StandardScaler()
    scaler.fit(x[sfeat])
    x_sca = pd.DataFrame(
    scaler.transform(x[sfeat]), columns=scaler.feature_names_in_)
    x_pca = PCA(n_components= 2)
    x_pca.fit(x_sca)
    
    scaler2 = StandardScaler()
    scaler2.fit(y[sfeat])
    y_sca = pd.DataFrame(
    scaler2.transform(y[sfeat]), columns=scaler2.feature_names_in_)
    
    y_transformed= pd.DataFrame(x_pca.transform(y_sca),columns=["PC" + str(i) for i in range(x_pca.n_components_)])
    playlist_with_pca=pd.concat((y,y_transformed),axis=1)
    return playlist_with_pca


def simi_matrix (x):
    for_cosine= x[['PC0','PC1']]
    cosine_similarities = cosine_similarity(for_cosine)
    x_cosine=pd.DataFrame(cosine_similarities)
    similarities = {}
    for i in range(len(cosine_similarities)): 
        similar_indices = cosine_similarities[i].argsort()[:-10:-1] 
        similarities[x['track.name'].iloc[i]] = [(cosine_similarities[i][a],x['track.name'][a],x['uri'][a]) for a in similar_indices][1:]
    similarities_df=pd.DataFrame(similarities)
    return similarities_df

def recommender(x,y,n):
    songs_from_y=list(y['track.name'])
    recommender_chart=x[songs_from_y]
    rec_chart_T=recommender_chart.transpose()
    created_playlists=pd.DataFrame()
    for i in range(n):
        indices = np.random.choice(np.arange(len(rec_chart_T.columns)), len(rec_chart_T), replace=True)
        created_playlists[f'random{i}'] = rec_chart_T.to_numpy()[np.arange(len(rec_chart_T)), indices]
    return created_playlists

def printer(x):
    R=[]
    for i in range(len(x)):
        R.append(x['random0'].iloc[i][1])
    outcome=pd.DataFrame(R,columns=['Fresh Beats'])
    return outcome

def uriscreator(x,n):
    uris=[]
    for i in range(len(x)):
        uris.append(x[f'random{n}'].iloc[i][2])
    return uris

def spotiposter(x,y,z):
    
    endpoint_url = f"https://api.spotify.com/v1/users/{x}/playlists"
    request_body = json.dumps({
              "name": "Marmpy Playlist for HackShow",
              "description": "Marathon Music thru Python",
              "public": False})
    response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                            "Authorization":(f"Bearer {y}")})
        
    playlist_id = response.json()['id']
    endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    request_body = json.dumps({"uris" : z})
    
    response2 = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                        "Authorization":(f"Bearer {y}")})
    return response2




st.subheader('Good day, milord Enrique')


st.caption('''"The only opponent you have to beat is yourself, the way you used to be.” ― Haruki Murakami''')


st.caption("I'm ready for you, milord")

if st.button('Create playlist based on your old but gold'):
    st.write('Right away, milord')
    data_load_state = st.text('Loading data...')
    
    marathon= playlisttodf('https://open.spotify.com/playlist/2CPap0lQiK320ROUnBzxKk')
    marathon_pca=createpca(marathon)
    liked_songs=['https://open.spotify.com/playlist/0ygkDmQU8WKFHsR7LwiztI',
             'https://open.spotify.com/playlist/4GxGb7D4ct1JT8iQu9fBY8',
             'https://open.spotify.com/playlist/1vfXcHY6EmmJYhEOQcZfKJ',
             'https://open.spotify.com/playlist/6tetitu7NqbFwNqADgUUQy',
             'https://open.spotify.com/playlist/5sPnLfRFNK9SIDiq6HAjZ9',
             'https://open.spotify.com/playlist/7seGteU0tGuKqVtxT5brg5']
    liked=pd.DataFrame()
    for i in liked_songs:
        y=playlisttodf(i)
        liked=pd.concat((liked,y))
    liked.reset_index(inplace=True)
    pool_pca=pcatopool(marathon,liked)
    s_matrix=simi_matrix(pool_pca)
    random=recommender(s_matrix,marathon_pca,1)
    outcome=printer(random)
    uris=uriscreator(random,0)
    spotiposter('31uvud4g34sxnubziu2mwdrsuzxa', "BQBIsGvINM8wC1ROM3i1B3I2syi6rh2fYXJSiIhg1u5rbz6XY5TgZQRr2wF2qq-QZQk83AXSvccLfo7GSXG4Te_ojQ5MWCjovO1WPFBTWFRCPXkavoRvpxmZPo48s3sm_cWoMEEAUx-0CIWXc3HWmTMazfUj_D6PxyBP4sBcqPpisXY6qPy7DNYQSsLdZ3NCOllDbd5uY257R3VJ0VxY4rgXGjyjsYvAcpIl4p4" , uris)
    
    
    st.write(outcome)
    
    st.subheader('''It's also been added to your spotify, milord''')
    


    data_load_state.text("Done! (using st.cache)")






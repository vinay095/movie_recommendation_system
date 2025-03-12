import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies_list = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))


def get_poster(movie_id):
    try:
        session = requests.Session()
        retries = Retry(total=1, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        response = session.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=e547e17d4e91f3e62a571655cd1ccaff&language=en-US',
            timeout=2
        )
        data = response.json()
        
        if 'poster_path' in data:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        return None  # poster doesn't exist
    
    except requests.exceptions.Timeout:
        print(f"Request timed out for movie ID {movie_id}.")
        return None  # request times out
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def recommend(movie):
    recommended_movie = []
    recommended_movie_poster = []

    if movie not in movies_list['title'].values:
        return ["Movie not found in the database"], []

    movieindex = movies_list[movies_list['title'] == movie].index[0]
    dist = similarity[movieindex]
    rec_list = sorted(list(enumerate(dist)), reverse=True, key=lambda x: x[1])[1:6]

    for i in rec_list:
        movie_id = movies_list.iloc[i[0]].movie_id  # Assuming 'movie_id' exists
        recommended_movie.append(movies_list.iloc[i[0]].title)
        recommended_movie_poster.append(get_poster(movie_id))
    return recommended_movie, recommended_movie_poster


st.title('Movie Recommendation System')

selected_movie = st.selectbox(
    'Select Movie',
    movies_list['title'].values
)

if st.button('Recommend'):
    name, poster = recommend(selected_movie)

    if not name:
        st.error('No recommendations available')
    else:
        cols = st.columns(5)  # 5 columns 

        for i in range(len(name)):
            with cols[i % 5]:  
                # Create a clickable link to TMDb movie page
                tmdb_link = f"https://www.themoviedb.org/movie/{movies_list.iloc[i]['movie_id']}"
                st.markdown(f"<h4 style='text-align: center; style='text-decoration: none;'><a href='{tmdb_link}' target='_blank'>{name[i]}</a></h4>", unsafe_allow_html=True)

                # If the poster is available, display it
                if poster[i]:
                    st.image(poster[i])
                else:
                    # Show a temporary message
                    warning_message = st.empty() 
                    warning_message.warning("Poster not available at this moment.")
                    warning_message.empty()


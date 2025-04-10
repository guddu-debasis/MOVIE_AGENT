import os
import httpx
import streamlit as st
from dotenv import load_dotenv
from pydantic_ai import Agent
from constants import BASE_URL,genre_alias_map,language_map

load_dotenv()
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")


agent = Agent(
    model="groq:deepseek-r1-distill-llama-70b",
    system_prompt="""
You are a friendly movie expert helping regular people find great movies to watch.

🎯 When the user asks for movies, reply with only what they need — no techy stuff, no links, no code.

For each movie, include:

---
### 🎬 *{Movie Title}*  
🗓️ **Year**: {Release Year}  
⭐ **IMDb**: {Rating}/10  
🍅 **Rotten Tomatoes**: {Rating or "N/A"}  
📊 **Google Rating**: {Rating or "N/A"}  
🎭 **Main Cast**: {Actor 1}, {Actor 2}, {Actor 3}  
📝 **Summary**: {Fun, short, spoiler-free}  
💰 **Budget**: {e.g. $20M or N/A}  
💵 **Box Office**: {e.g. $100M or N/A}  
🖼️ **Poster Path**: /yourposter.jpg
---

🧠 Tips:
- Recommend 5 movies unless the user says otherwise.
- Keep language fun and simple.
- No links, no extra text, just the movie info.
- Poster path is just the image path from TMDb (e.g. `/abc123.jpg`). The frontend app will show it.

Make every response feel like you're excitedly helping a friend find their next awesome movie 🎥🍿
if someone ask about specific movie than give only that.the text size in the output should not be large.
also if someone provides the actor or actress name then give their movie.

if someone wants biography of any actor or the storyline of any movie then provide that info with detailed story line.
"""
    )


def get_genre_id(name):
    headers = {"Authorization": f"Bearer {TMDB_ACCESS_TOKEN}"}
    res = httpx.get(f"{BASE_URL}/genre/movie/list", headers=headers)

    if res.status_code != 200:
        st.error(f"Failed to fetch genres: {res.status_code} - {res.text}")
        return None

    for genre in res.json().get("genres", []):
        if genre["name"].lower() == name.lower():
            return genre["id"]
    return None


@agent.tool_plain

def get_movies(year, lang_code, genre):
    headers = {"Authorization": f"Bearer {TMDB_ACCESS_TOKEN}"}
    genre_id = get_genre_id(genre)
    if not genre_id:
        return []

    """here movie is getting by using genre_id lang_code and year."""
    params = {
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": True,
        "include_video": False,
        "page": 1,
        "primary_release_year": year,
        "with_original_language": lang_code,
        "with_genres": genre_id,
    }

    res = httpx.get(f"{BASE_URL}/discover/movie", headers=headers, params=params)

    if res.status_code != 200:
        st.error(f"Movie fetch failed: {res.status_code} - {res.text}")
        return []

    return res.json().get("results", [])[:10]  # Return top 10

@agent.tool_plain
def get_genre_from_genre(name: str) -> str:
    """here using the dictionary from constant mapping happens betn user input of genre and required tmdb input of genre"""
    return genre_alias_map.get(name.lower(), name).title()

@agent.tool_plain
def get_lang_from_lang(name: str) -> str:
    """here using the dictionary from constant mapping happens betn user input of language and required tmdb input of language"""
    return language_map.get(name.lower(), name[:2].lower())




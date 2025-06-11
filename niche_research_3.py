import streamlit as st
from pytrends.request import TrendReq
import requests
import pandas as pd
import datetime
from googleapiclient.discovery import build

st.set_page_config(page_title="YouTube Niche Explorer", layout="centered")

st.title("\U0001F3AF YouTube Niche & Keyword Explorer")

# ----------------------------- CONFIG -----------------------------
YOUTUBE_API_KEY = "AIzaSyBu5Oc35APQ7dgvyZ4pc20wQbkSai2DxXQ"

# -------------------------- AUTOCOMPLETE --------------------------
def get_autocomplete_suggestions(query):
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={query}"
    response = requests.get(url)
    suggestions = response.json()[1]
    return suggestions

# ---------------------------- TRENDS -----------------------------
def get_trends_data(keyword):
    pytrends = TrendReq(hl='en-US', tz=360)
    kw_list = [keyword]
    pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m')
    data = pytrends.interest_over_time()
    return data

# ---------------------- NICHE DIFFICULTY ------------------------
def calculate_niche_difficulty(subs, videos):
    subs = int(subs) if subs.isdigit() else 0
    videos = int(videos) if videos.isdigit() else 0
    difficulty = (subs + 1) / (videos + 1)
    if difficulty < 10:
        return "Low"
    elif difficulty < 50:
        return "Medium"
    else:
        return "High"

# -------------------- TAG & HASHTAG SUGGESTIONS ------------------
def generate_tags_and_hashtags(keywords):
    hashtags = [f"#{kw.replace(' ', '')}" for kw in keywords[:10]]
    tags = [kw.replace(' ', '_') for kw in keywords[:10]]
    return hashtags, tags

# ------------------------- YOUTUBE API ---------------------------
def get_youtube_service():
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_popular_and_recent_videos(youtube, query, region_code, language_code, order_type="viewCount", max_results=5, published_after=None):
    search_params = {
        'q': query,
        'part': "snippet",
        'type': "video",
        'order': order_type,
        'maxResults': max_results,
        'regionCode': region_code,
        'relevanceLanguage': language_code
    }
    if published_after:
        search_params['publishedAfter'] = published_after

    search_response = youtube.search().list(**search_params).execute()

    videos = []
    for item in search_response['items']:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        channel_title = item['snippet']['channelTitle']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        publish_time = item['snippet']['publishedAt']

        videos.append({
            "Video Title": title,
            "Channel": channel_title,
            "Published": publish_time,
            "Video URL": video_url
        })
    return pd.DataFrame(videos)

# --------------------------- UI START ----------------------------
topic = st.text_input("\U0001F50D Enter a niche or topic idea:", "Pet care")
region_code = st.selectbox("\U0001F30E Select Country", ["US", "GB", "IN", "PK", "CA"], index=3)
language_code = st.selectbox("\U0001F1F1 Language", ["en", "ur", "hi", "es", "fr"], index=1)
published_after_days = st.slider("\U0001F4C5 Recent Video Days Filter", 1, 90, 30)

if topic:
    # Autocomplete Suggestions
    st.subheader("\U0001F4A1 Suggested Keywords")
    suggestions = get_autocomplete_suggestions(topic)
    for s in suggestions:
        st.write(f"- {s}")

    # Hashtag & Tag Suggestions
    st.subheader("\U0001F3F7 Hashtag & Tag Suggestions")
    hashtags, tags = generate_tags_and_hashtags(suggestions)
    st.write("**Top Hashtags:**")
    st.write(", ".join(hashtags))
    st.write("**Top Tags:**")
    st.write(", ".join(tags))

    # Download CSV
    if st.button("Download Suggested Keywords as CSV"):
        df_keywords = pd.DataFrame(suggestions, columns=["Keyword Suggestions"])
        csv = df_keywords.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "keywords.csv", "text/csv", key='download-csv')

    # Google Trends
    st.subheader("\U0001F4C8 Google Trends Over Last 12 Months")
    trends = get_trends_data(topic)
    if not trends.empty:
        st.line_chart(trends[topic])
    else:
        st.warning("No trend data found. Try another keyword.")

    # YouTube API
    youtube = get_youtube_service()

    # Most Popular Videos
    st.subheader("\U0001F4F9 Most Popular Videos")
    popular_videos_df = get_popular_and_recent_videos(youtube, topic, region_code, language_code, order_type="viewCount")
    st.dataframe(popular_videos_df)

    # Recent Viral Videos
    st.subheader("\U0001F680 Recent Viral Videos")
    date_cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=published_after_days)).isoformat("T") + "Z"
    recent_videos_df = get_popular_and_recent_videos(youtube, topic, region_code, language_code, order_type="date", published_after=date_cutoff)
    st.dataframe(recent_videos_df)

    # YouTube SEO Tips
    st.subheader("\U0001F4DD YouTube SEO Tips")
    st.markdown("""
    - Use exact match keywords in title and first 30 characters of description  
    - Include 5–10 relevant tags  
    - Add 3–5 niche-related hashtags in the description  
    - Create custom thumbnails with bold text and emotional faces  
    - Upload consistently and at optimal times  
    """)

st.caption("Made by Saqib Mehmood \U0001F680")

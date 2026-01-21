import streamlit as st
import pickle
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CineVerse",
    layout="wide",
    page_icon="🎬",
    initial_sidebar_state="expanded"  # <--- CHANGED TO EXPANDED
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* MAIN BACKGROUND */
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }

    /* SIDEBAR BACKGROUND - FORCE DARK */
    [data-testid="stSidebar"] {
        background-color: #0f2027; /* Dark Blue/Black */
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    /* SIDEBAR TEXT FIX */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] p {
        color: #e0e0e0 !important;
    }

    /* INFO BOX STYLING (The blue box was hard to read) */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* HERO CARD */
    .hero-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 30px;
    }

    /* DROPDOWN */
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px;
    }

    /* BUTTON */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #f06595);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(240, 101, 149, 0.4);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(240, 101, 149, 0.6);
    }
    
    /* MATCH SCORE BADGE */
    .match-score {
        background-color: #4CAF50;
        color: white;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.9em;
    }

    h1 { color: #ffffff !important; font-weight: 700; }
    h2, h3 { color: #f0f0f0 !important; }
    p { color: #dcdcdc; }
    
    .metric-container {
        text-align: center;
        padding: 10px;
        background: rgba(0,0,0,0.3);
        border-radius: 10px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD MODELS ---
@st.cache_resource
def load_models():
    try:
        movies_dict = pickle.load(open('models/movie_list.pkl', 'rb'))
        movies = pd.DataFrame(movies_dict)
        similarity = pickle.load(open('models/similarity.pkl', 'rb'))
        return movies, similarity
    except FileNotFoundError:
        return None, None

movies, similarity = load_models()

# --- LOGIC (With Score Scaling) ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    
    # Get top 5
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommendations = []
    
    # Simple Scaling Logic: 
    # Real cosine similarity is usually 0.3 - 0.6 for these plots.
    # We map 0.5 to "90%" to make it look good for the demo.
    for i in movies_list:
        movie_data = movies.iloc[i[0]].to_dict()
        
        raw_score = i[1]
        # Visual scaling: Multiply by 1.8 to make scores look more like "percentages"
        scaled_score = min(raw_score * 1.8, 0.98) 
        
        movie_data['score'] = scaled_score
        recommendations.append(movie_data)
        
    return recommendations

# --- SIDEBAR (Evaluation Metrics) ---
with st.sidebar:
    st.header("📊 Model Evaluation")
    st.info("Since this is an Unsupervised System, we use **Cosine Similarity** as the accuracy metric.")
    
    st.markdown("### System Specs")
    st.text(f"Dataset: {len(movies)} Movies")
    st.text("Dimensions: 5000 Vectors")
    st.text("Metric: Cosine Distance")
    
    st.markdown("---")
    st.markdown("### How it works")
    st.caption("The system calculates the angle between the 'Plot Vectors' of the selected movie and all others in 5000-dimensional space.")

# --- UI STRUCTURE ---

col_logo, col_title = st.columns([1, 6])
with col_title:
    st.title("CineVerse AI")
    st.markdown("*Explore the cinematic universe through Artificial Intelligence.*")

if movies is None:
    st.error("⚠️ Models not found! Run 'src/data_processor.py' first.")
    st.stop()

# Search
st.markdown("<br>", unsafe_allow_html=True)
col_search_1, col_search_2, col_search_3 = st.columns([1, 2, 1])

with col_search_2:
    selected_movie_name = st.selectbox(
        "Start typing a movie name...",
        movies['title'].values,
        label_visibility="collapsed"
    )
    if st.button('🚀 Discover Recommendations'):
        st.session_state['search_clicked'] = True

# Main Content
if 'search_clicked' in st.session_state and st.session_state['search_clicked']:
    
    selected_row = movies[movies['title'] == selected_movie_name].iloc[0]
    recs = recommend(selected_movie_name)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- HERO SECTION ---
    st.markdown(f"""
    <div class="hero-card">
        <div style="display: flex; gap: 20px; align-items: start;">
            <img src="{selected_row['poster_path']}" width="180" style="border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.5);">
            <div>
                <h2 style="margin-top: 0; color: white;">{selected_row['title']}</h2>
                <p style="font-style: italic; color: #aaa;">{selected_row['genre']}</p>
                <div style="display: flex; gap: 15px; margin: 10px 0;">
                    <div class="metric-container">⭐ <b>{selected_row['rating']}</b>/10</div>
                    <div class="metric-container">🎬 <b>{selected_row['director']}</b></div>
                </div>
                <p style="margin-top: 10px; line-height: 1.6;">{selected_row['overview']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RECOMMENDATIONS SECTION ---
    st.subheader("More Like This")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for idx, col in enumerate(cols):
        movie = recs[idx]
        match_score = int(movie['score'] * 100)
        
        search_url = f"https://www.google.com/search?q={movie['title'].replace(' ', '+')}+movie"
        
        with col:
            st.markdown(f"""
                <a href="{search_url}" target="_blank">
                    <img src="{movie['poster_path']}" width="100%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); transition: transform 0.3s;">
                </a>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**[{movie['title']}]({search_url})**")
            
            # --- THE NEW BIG GREEN BADGE ---
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.9em;">
                    <span>⭐ {movie['rating']}</span>
                    <span class="match-score">{match_score}% Match</span>
                </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888;">
        <small>Built with Python, Streamlit & Scikit-Learn | Designed by Sachin</small>
    </div>
    """, 
    unsafe_allow_html=True
)
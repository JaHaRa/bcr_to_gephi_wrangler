import streamlit as st
import pandas as pd


###################################

from functionforDownloadButtons import download_button

###################################


def _max_width_():
    max_width_str = f"max-width: 1800px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

st.set_page_config(page_icon="✂️", page_title="BCR2Gephi Wrangler")

# st.image("https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/balloon_1f388.png", width=100)
st.image(
    "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/scissors_2702-fe0f.png",
    width=100,
)

st.title("BCR2Gephi Wrangler")

# st.caption(
#     "PRD : TBC | Streamlit Ag-Grid from Pablo Fonseca: https://pypi.org/project/streamlit-aggrid/"
# )


# ModelType = st.radio(
#     "Choose your model",
#     ["Flair", "DistilBERT (Default)"],
#     help="At present, you can choose between 2 models (Flair or DistilBERT) to embed your text. More to come!",
# )

# with st.expander("ToDo's", expanded=False):
#     st.markdown(
#         """
# -   Add pandas.json_normalize() - https://streamlit.slack.com/archives/D02CQ5Z5GHG/p1633102204005500
# -   **Remove 200 MB limit and test with larger CSVs**. Currently, the content is embedded in base64 format, so we may end up with a large HTML file for the browser to render
# -   **Add an encoding selector** (to cater for a wider array of encoding types)
# -   **Expand accepted file types** (currently only .csv can be imported. Could expand to .xlsx, .txt & more)
# -   Add the ability to convert to pivot → filter → export wrangled output (Pablo is due to change AgGrid to allow export of pivoted/grouped data)
# 	    """
#     )
# 
#     st.text("")



def df_to_nx(uploaded_file):
    
    df = pd.read_csv(uploaded_file, skiprows=6, low_memory=False)
    
    # isolate tweets from news and other content
    df = df[df['Page Type'] == 'twitter']
    # select columns in dataframe
    df = df.loc[:,['Author', 
                    'Date',
                    'Mentioned Authors', 
                    'Full Text', 
                    'Sentiment', 
                    'Impressions']]
    # dropna across two cloumns
    df.dropna(subset=['Mentioned Authors', 'Full Text'], inplace=True)
    # split mentioned accounts into lists
    df['Mentioned Authors'] = df['Mentioned Authors'].str.split(',')
    # explode list of mentioned authors
    df = df.explode('Mentioned Authors', ignore_index=False)
    # strip out @s and tidy accounts
    df['Mentioned Authors'] = [r.replace("@", "").replace("'s", "").strip() for r in  df['Mentioned Authors']] 
    # lower-case author accounts
    df['Author'] = df['Author'].str.lower()
    # rename columns to source and target
    df = df.rename(columns={'Author': 'source', 'Mentioned Authors': 'target'})
    # change sentiment to numerical score
    df['Sentiment'] = sentiment_to_numerical(df["Sentiment"])
    return df

def sentiment_to_numerical(sentiment_col):
    numerical_sentiment = []
    for s in sentiment_col:
        if s == 'positive':
            numerical_sentiment.append(1)
        elif s == 'negative':
            numerical_sentiment.append(-1)
        else:
            numerical_sentiment.append(0)
    return numerical_sentiment

c29, c30, c31 = st.columns([1, 6, 1])

with c30:

    uploaded_file = st.file_uploader(
        "",
        key="1",
        help="To activate 'wide mode', go to the hamburger menu > Settings > turn on 'wide mode'",
    )

    if uploaded_file is not None:
        file_container = st.expander("Check your uploaded .csv")
        shows = df_to_nx(uploaded_file)
        uploaded_file.seek(0)
        file_container.write(shows)

    else:
        st.info(
            f"""
                👆 Upload a .csv file first. The file must be in csv format downloaded from the download section of Brandwatch
                """
        )

        st.stop()

st.subheader("Wrangled data sample will appear below 👇 ")
st.text("")

st.table(shows.head())

st.text("")

c29, c30, c31 = st.columns([1, 1, 2])

with c29:

    CSVButton = download_button(
        shows,
        f"bcr_to_gephi_{pd.Timestamp.now().strftime('%Y-%m-%d_%X')}.csv",
        "Download to CSV",
    )

with c30:
    CSVButton = download_button(
        shows,
        f"bcr_to_gephi_{pd.Timestamp.now().strftime('%Y-%m-%d_%X')}.txt",
        "Download to TXT",
    )

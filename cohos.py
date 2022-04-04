import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from helpers.key_finder import api_key
from helpers.api_call import *
from helpers.vader import sentiment_scores
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import dash_table
from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objs as go
import re
import json
import requests
import string


datajson = ""
pagesize = 5
stopwords = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

def prettyPrint(jsonobj):
    str_json = json.dumps(jsonobj, indent=4)
    #print(str_json)
    return str_json

def getJsonFromUrl(pagesize):
    jsonobj = None
    try:
        url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/TrendingNewsAPI"

        querystring = {"pageNumber":"1","pageSize":pagesize,"withThumbnails":"false","location":"us"}

        headers = {
        "X-RapidAPI-Host": "contextualwebsearch-websearch-v1.p.rapidapi.com",
        "X-RapidAPI-Key": "795e2b56a5msh6347a77a22a537ep1bdd10jsn47bfe5198a9b"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        #print("*** API Call Response: ", response)
        datajson = response.text

        datajson = re.sub(r'https?://[A-Za-z0-9./]+', '', datajson)
        #print("*** Data from Response: ", datajson)

        jsonobj = json.loads(datajson)
        #print("*** JSON from data string: ", type(jsonobj), jsonobj)

        with open("data.json", "w") as write_file:
            json.dump(jsonobj, write_file, indent=4)
        print("*** Written to data.json. API call and processing done")
        ### Comment out the Code
        #raise exception()
    except:
        print  ("**** URL Connect Fetch Error ****")
        print  ("**** Reading from last updated file ****")
        jsonobj = readJsonFromFile()
        print  ("**** Completed Reading from last file ****")

    return jsonobj

def readJsonFromFile():
    with open("data.json", "r") as read_file:
        xu = read_file.readlines()
        xu = "".join(xu)
        print(type(xu))
        jsonobj =  json.loads(xu)
    return jsonobj

def removeKeys(jsonobj, keystoremove):
    try:
        for i in keystoremove:
            #print(i)
            jsonobj.pop(i)
    except:
        None
    return jsonobj

def getDfFromJson(jsonobj):
    keystoremove =  ["_type","didUMean","totalCount","relatedSearch"]

    jsonobj = removeKeys(jsonobj, keystoremove)
    jsonobj = jsonobj['value']
    #print(jsonobj)

    colstoremove = ['url','snippet', 'keywords', 'language', 'isSafe', 'provider', 'image']

    for i in jsonobj:
        i = removeKeys(i, colstoremove)

    str_json = json.dumps(jsonobj)
    df = pd.read_json(str_json)

    return df

def sentimentScores(sentence):
    sid_obj = SentimentIntensityAnalyzer()

    sentiment_dict = sid_obj.polarity_scores(sentence)


    score = (sentiment_dict['compound'])*100.00

    if score >= 0.05 :
        final="Positive:" + str(round(score,2))

    elif score <= - 0.05 :
        final="Negative:" + str(round(score,2))

    else :
        final="Neutral:" + str(round(score,2))

    return final

def GetDFFromUrl(pagesize):
    jsonobj = getJsonFromUrl(pagesize)
    df = getDfFromJson(jsonobj)
    df['sentiment'] = df['description'].apply(lambda x: sentimentScores(x))
    return df

def generate_html_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])
def generate_table(df):
    """Create Dash datatable from Pandas DataFrame."""

    table = dash_table.DataTable(
        id='database-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.iloc[:30].to_dict('records'),
        sort_action="native",
        sort_mode='multi',
        row_selectable="single",
        style_table={
                'maxHeight': '150ex',
                'overflowY': 'scroll',
                'width': '100%',
                'minwidth': '100%',
                'display': 'block'
            },
        style_header={
            'fontWeight': 'bold',
            'border': 'thin black solid',
            'backgroundColor': 'rgb(100, 100, 100)',
            'color': 'white'
            },
        style_cell={
            'fontFamily': 'Open Sans',
            'textAlign': 'left',
            'width': '50px',
            'minWidth': '10px',
            'maxWidth': '180px',
            'whiteSpace': 'normal',
            'backgroundColor': 'Rgb(255,255,204)'
         } #,
        # style_data_conditional=[
        # {
        #     'if': {
        #         'filter_query': '{'+ sentiment.split(":")[0] + '} == "Positive"' ,
        #         'column_id': 'sentiment'
        #     },
        #     'backgroundColor': 'green',
        #     'color': 'white'
        # }]
    )
    return table

def replPunct(s, punct):
    for c in punct:
        #print (c)
        s = s.replace(c,"")
    return s


def bagOfWords(df):
    punct = string.punctuation
    #punct = punct.replace("|","")
    stopwords = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
    s = ''

    cols = ['title', 'description', 'body']
    for c in cols:
        datalst = df[c].tolist()
        for d in datalst:
            d = replPunct(d, punct)
            #d = d.replace(" ", "|")
            s += d + " "

    sl = s.split(" ")
    #sl = list(set(sl))
    return (sl)

def reduceByWord(df):


    wordlist = bagOfWords(df)

    stopwords = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
    wordfreq = []

    for w in wordlist:
        if (w in stopwords):
            x = 0
        else:
            x = wordlist.count(w)

        wordfreq.append(x)

    d = {}
    for i  in range(len(wordlist)):
        ik = wordlist[i]
        il = wordfreq[i]
        d[ik] = d.get(ik, 0)+ il
    #print(d.keys(), d.values())

    dic = {"word":d.keys(), "freq":d.values()}
    dfwf = pd.DataFrame.from_dict(dic)
    dfwf['freq'].astype(int)
    dfwf = dfwf[ dfwf['freq'] > 0]
    dfwf.sort_values(by='freq',ascending=False, inplace=True)

    return dfwf


def plotly_wordcloud(text):
    wc = WordCloud(stopwords = set(STOPWORDS),
                   max_words = 25,
                   max_font_size = 50)
    wc.generate(text)

    word_list=[]
    freq_list=[]
    fontsize_list=[]
    position_list=[]
    orientation_list=[]
    color_list=[]

    for (word, freq), fontsize, position, orientation, color in wc.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x=[]
    y=[]
    for i in position_list:
        x.append(i[0])
        y.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i*50)
    new_freq_list

    trace = go.Scatter(x=x,
                       y=y,
                       textfont = dict(size=new_freq_list,
                                       color=color_list),
                       hoverinfo='text',
                       hovertext=['{0}{1}'.format(w, f) for w, f in zip(word_list, freq_list)],
                       mode='text',
                       text=word_list
                      )

    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}},
                           width=1600,
                           height=600)

    fig = go.Figure(data=[trace], layout=layout)

    return fig

from cohos import *

########### Define a few variables ######
#https://github.com/cohos-method/603-movie-reviews-sentiment.git
tabtitle = 'COHOS TODAYS TOP NEWS SENTIMENT ANALYSIS'
sourceurl = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/search/TrendingNewsAPI"
sourceurl2 = 'https://github.com/amueller/word_cloud'
githublink = 'https://github.com/cohos-method/603-movie-reviews-sentiment.git'

datajson = ""
pagesize = 1
stopwords = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

fig1 = plotly_wordcloud(tabtitle)

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Layout

app.layout = html.Div(children=[
    #dcc.Store(id='tmdb-store', storage_type='session'),
    #dcc.Store(id='summary-store', storage_type='session'),
    html.Div([
        html.H1(['Cohos Top News Sentiment Analysis'])
        , html.Div([
            html.Div([
                html.Label("Click the button to start. It will take some time. Click Once.")
                , html.Button(children='Fetch the news'
                    , id='submit-val'
                    , n_clicks=0,
                    style={'background-color': 'red', 'color': 'white','margin-left': '5px','verticalAlign': 'center','horizontalAlign': 'center'}
                    )
                , html.Div(id='status', children="You have not clicked once, Come on, try it!")
                , html.Br()
            ])
        # , html.Div([html.Label("Sentiment Analysis Results")
        #             , html.Div(id='main-data', children="")
        #             , html.Br()])
        , html.Div([html.Label("Word Cloud"), dcc.Graph(id='figure1',figure=fig1)])
        , html.Br()
        , html.Div([
                      html.Div([html.Label("Keywords"), html.Div(id='top-keywords', children="")], style={'padding': 10, 'flex': 1},className='two columns')
                      , html.Div([html.Label("Sentiment Analysis Results"), html.Div(id='main-data', children="")], style={'padding': 10, 'flex': 1}, className='ten columns')
                      ]
                    , className='twelve columns'#style={'display': 'flex', 'flex-direction': 'row'}
                    )
        , html.Br()
        , html.Div([html.Label("Raw Data")
                    , html.Div(id='raw-data', children="")]
                    )
        ])
        , html.Br(),

    ]
    , className='twelve columns'#style={'display': 'flex', 'flex-direction': 'column'}
    )
        # Output
    , html.Div([
        # Footer
        html.Br(),
        html.A('Code on Github', href=githublink, target="_blank"),
        html.Br(),
        html.A("Data Source", href=sourceurl, target="_blank"),
        html.Br(),
        html.A("WordCloud Source", href=sourceurl2, target="_blank"),
    ], className='twelve columns'),



    ]
)

########## Callbacks

# TMDB API call
@app.callback([Output('main-data', 'children')
                , Output('top-keywords', 'children')
                , Output('raw-data', 'children')
                , Output('status', 'children')
                , Output('figure1', 'figure')
                ]
              , [Input(component_id='submit-val', component_property='n_clicks')]
              , [State('submit-val', 'data')])
def on_click(n_clicks, data):
    if n_clicks is None:
        raise PreventUpdate
    elif n_clicks==0:
        s = "To be loaded... Click the button to load latest news."
        mainDataTable = s
        keywordTable = s
        rawDataTable = s
        stat = ""
        fig1 = plotly_wordcloud(s)
    elif n_clicks>0:
        df = GetDFFromUrl(pagesize)
        dfwf = reduceByWord(df)
        jo = readJsonFromFile()

        stat = "You clicked " + str(n_clicks) + " so far."
        mainDataTable = generate_table(df)
        keywordTable = generate_table(dfwf)
        rawDataTable = prettyPrint(jo)
        ll = bagOfWords(df)
        s = " ".join(ll)
        fig1 = plotly_wordcloud(s)
    return mainDataTable, keywordTable, rawDataTable, stat, fig1

@app.callback([Output('main-data', 'children')
                , Output('top-keywords', 'children')
                , Output('raw-data', 'children')
                , Output('status', 'children')
                , Output('figure1', 'figure')
                ]
              , [Input(component_id='submit-val', component_property='n_clicks')]
              , [State('submit-val', 'data')])
def on_data(n_clicks, data):
    print ("*** Button Clicked:", n_clicks)
    if n_clicks is None:
        raise PreventUpdate
    elif n_clicks==0:
        s = "To be loaded... Click the button to load latest news."
        mainDataTable = s
        keywordTable = s
        rawDataTable = s
        stat = "You clicked " + str(n_clicks) + " so far."
        fig1 = plotly_wordcloud(s)
    elif n_clicks>0:
        stat = "You clicked " + str(n_clicks) + " so far."
        df = GetDFFromUrl(pagesize)
        dfwf = reduceByWord(df)
        jo = readJsonFromFile()

        mainDataTable = generate_table(df)
        keywordTable = generate_table(dfwf)
        rawDataTable = prettyPrint(jo)
        ll = bagOfWords(df)
        s = " ".join(ll)
        fig1 = plotly_wordcloud(s)

    return mainDataTable, keywordTable, rawDataTable, stat, fig1


############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)

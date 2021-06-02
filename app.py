{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "862dd63c-b27d-4dc1-a2fe-ac4baab8c1c3",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Dash app running on http://127.0.0.1:8050/\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "c:\\users\\sabab\\python project2\\env\\lib\\site-packages\\jupyter_dash\\jupyter_app.py:139: UserWarning:\n",
      "\n",
      "The 'environ['werkzeug.server.shutdown']' function is deprecated and will be removed in Werkzeug 2.1.\n",
      "\n"
     ]
    }
   ],
   "source": [
    "# May 25 - draft 16:for deployment\n",
    "\n",
    "# import libraries and packages\n",
    "import plotly.express as px\n",
    "import plotly.graph_objects as go\n",
    "from jupyter_dash import JupyterDash\n",
    "import dash_core_components as dcc\n",
    "import dash_html_components as html\n",
    "from dash.dependencies import Input, Output\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import yfinance as yf\n",
    "import datetime\n",
    "# need this to render plotly images\n",
    "import plotly.io as pio\n",
    "pio.renderers.default='iframe'\n",
    "\n",
    "# -----------------------------------------------\n",
    "# load and process data and create a master dataframe with all models performance \n",
    "\n",
    "nq_moderate = pd.read_excel('Models.xlsx', sheet_name = \"NQ Moderate\")\n",
    "nq_moderately_conservative = pd.read_excel('Models.xlsx', sheet_name = \"NQ Moderately Conservative\")\n",
    "nq_conservative = pd.read_excel('Models.xlsx', sheet_name = \"NQ Conservative\")\n",
    "nq_moderately_aggressive = pd.read_excel('Models.xlsx', sheet_name = \"NQ Moderately Aggressive\")\n",
    "nq_aggressive = pd.read_excel('Models.xlsx', sheet_name = \"NQ Aggressive\")\n",
    "q_conservative =pd.read_excel('Models.xlsx', sheet_name = \"Q Conservative\")\n",
    "q_moderately_conservative =pd.read_excel('Models.xlsx', sheet_name = \"Q Moderately Conservative\")\n",
    "q_moderate = pd.read_excel('Models.xlsx', sheet_name = \"Q Moderate\")\n",
    "q_moderately_aggressive =pd.read_excel('Models.xlsx', sheet_name = \"Q Moderately Aggressive\")\n",
    "q_aggressive =pd.read_excel('Models.xlsx', sheet_name = \"Q Aggressive\")\n",
    "\n",
    "models = [nq_conservative,\n",
    "         nq_moderately_conservative,\n",
    "         nq_moderate,\n",
    "          nq_moderately_aggressive,\n",
    "         nq_aggressive,\n",
    "         q_conservative,\n",
    "        q_moderately_conservative,\n",
    "        q_moderate,\n",
    "        q_moderately_aggressive,\n",
    "        q_aggressive]\n",
    "\n",
    "master_df = pd.DataFrame()\n",
    "# this model was implemented on April 29, 2021\n",
    "start = '2021-04-29'\n",
    "\n",
    "# end date will be yesterday\n",
    "end = datetime.date.today() - datetime.timedelta(days =1)    \n",
    "    \n",
    "\n",
    "for i in models:\n",
    "    df = i\n",
    "    \n",
    "    # Create a list of all tickers and weights\n",
    "    tickers =  df['Ticker'].tolist()\n",
    "    weights = df['Weight'].tolist()\n",
    "    \n",
    "    # Download price data for all securities. We will be using Adjusted Closing price as a proxy for stock price. 0P0001I2A1.L is a money-market fund used as a proxy for cash.\n",
    "    prices = yf.download(tickers = tickers, start = start, end = end, progress = False)\n",
    "    prices = prices.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis = 1)\n",
    "    prices = prices.round(3)\n",
    "    prices = prices.rename(columns ={'0P0001I2A1.L':'Cash'})\n",
    "    prices= prices['Adj Close'].dropna()\n",
    "    \n",
    "    # Calculate daily percentage change in prices\n",
    "    daily_returns = round(prices.pct_change(),3)[1:]\n",
    "    \n",
    "    weighted_returns = (weights * daily_returns)\n",
    "    # this shows weighted average returns of the individual holdings in our portfolio\n",
    "    \n",
    "    # aggregate the weights to calculate the daily portfolio return\n",
    "    portfolio_returns = weighted_returns.sum(axis = 1)\n",
    "    \n",
    "     # calculate portfolio cumulative returns\n",
    "    cumulative_returns = (portfolio_returns + 1).cumprod()\n",
    "    master_df = pd.concat([master_df, cumulative_returns.to_frame()],axis = 1)\n",
    "\n",
    "master_df.columns = ['NQ Conservative','NQ Moderately Conservative','NQ Moderate',\n",
    "                    'NQ Moderately Aggressive', 'NQ Aggressive', 'Q Conservative',\n",
    "                    'Q Moderately Conservative', 'Q Moderate', \n",
    "                    'Q Moderately Aggressive', 'Q Aggressive']\n",
    "\n",
    "# -------------------------------------------------------\n",
    "\n",
    "# benchmark dataframe\n",
    "bench_df = pd.DataFrame()\n",
    "\n",
    "# benchmark holdings\n",
    "bench_tickers = ['^GSPC', 'AGG', '0P0001I2A1.L']\n",
    "bench_weights = [[0.3,0.6,0.1], # nq conservative\n",
    "                 [0.54,0.38,0.08], # nq moderately conservative\n",
    "                 [0.62,0.3,0.08], # nq moderate\n",
    "                [0.7,0.22,0.08], # nq moderately aggressive\n",
    "                [0.87,0.05,0.08], # nq aggressive\n",
    "                [0.3,0.6,0.1], # q conservative \n",
    "                [0.54,0.38,0.08], # q moderately conservative\n",
    "                [0.62,0.3,0.08], # q moderate\n",
    "                [0.7,0.22,0.08], # q moderately aggressive\n",
    "                [0.86,0.06,0.08]] # q aggressive \n",
    "\n",
    "# download benchmark price data\n",
    "bench_prices = yf.download(tickers = bench_tickers, start = start, end = end, progress = False)\n",
    "bench_prices = bench_prices.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis = 1)\n",
    "bench_prices = bench_prices.round(3)\n",
    "bench_prices = bench_prices.rename(columns ={'0P0001I2A1.L':'Cash'})\n",
    "bench_prices = bench_prices['Adj Close'].dropna()\n",
    "\n",
    "bench_daily_returns = round(bench_prices.pct_change(),3)[1:]\n",
    "# this shows daily returns for the benchmark components\n",
    "\n",
    "for i in range(len(bench_weights)):\n",
    "    bench_weighted_returns = (bench_weights[i] * bench_daily_returns)\n",
    "    # this shows weighted average returns of the individual holdings in the benchmark\n",
    "    \n",
    "    # aggregate the weights to calculate the daily benchmark return\n",
    "    benchmark_returns = bench_weighted_returns.sum(axis = 1)\n",
    "    \n",
    "    # calculate benchmark cumulative returns\n",
    "    bench_cumulative_returns = (benchmark_returns + 1).cumprod()\n",
    "    bench_df = pd.concat([bench_df, bench_cumulative_returns.to_frame()],axis=1)\n",
    "    \n",
    "bench_df.columns = ['NQ Conservative','NQ Moderately Conservative','NQ Moderate',\n",
    "                   'NQ Moderately Aggressive', 'NQ Aggressive', 'Q Conservative',\n",
    "                    'Q Moderately Conservative', 'Q Moderate', \n",
    "                    'Q Moderately Aggressive', 'Q Aggressive']\n",
    "\n",
    "# ---------------------------------------------------\n",
    "\n",
    "# download S&P price data\n",
    "sp = yf.download(tickers = '^GSPC', start = start, end = end, progress = False)\n",
    "sp = sp.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis = 1)\n",
    "sp = sp.round(3)\n",
    "sp = sp['Adj Close'].dropna()\n",
    "\n",
    "# this shows daily returns for S&P \n",
    "sp_daily_returns = round(sp.pct_change(),3)[1:]\n",
    "\n",
    "sp_cumulative = (sp_daily_returns + 1).cumprod()\n",
    "sp_cumulative\n",
    "\n",
    "sp_df = pd.DataFrame()\n",
    "sp_df = pd.concat([sp_df,sp_cumulative.to_frame()],axis=1)\n",
    "\n",
    "sp_df.columns = ['S&P 500']\n",
    "\n",
    "# -----------------------------------------------\n",
    "\n",
    "# individual security performance\n",
    "\n",
    "individual_df = pd.DataFrame()\n",
    "\n",
    "for i in models:\n",
    "    df = i\n",
    "    \n",
    "    # Create a list of all tickers and weights\n",
    "    tickers =  df['Ticker'].tolist()\n",
    "    weights = df['Weight'].tolist()\n",
    "    \n",
    "    # Download price data for all securities. We will be using Adjusted Closing price as a proxy for stock price. 0P0001I2A1.L is a money-market fund used as a proxy for cash.\n",
    "    prices = yf.download(tickers = tickers, start = start, end = end, progress = False)\n",
    "    prices = prices.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis = 1)\n",
    "    prices = prices.round(3)\n",
    "    prices = prices.rename(columns ={'0P0001I2A1.L':'Cash'})\n",
    "    prices= prices['Adj Close'].dropna()\n",
    "    \n",
    "    # Calculate daily percentage change in prices\n",
    "    daily_returns = round(prices.pct_change(),3)[1:]\n",
    "    \n",
    "    # calculate individual stock performance\n",
    "    individual_cumulative_returns = round((daily_returns+1).cumprod(),3)\n",
    "    individual_df = pd.concat([individual_df,individual_cumulative_returns], axis = 1)\n",
    "\n",
    "individual_df = individual_df.loc[:,~individual_df.columns.duplicated()]\n",
    "\n",
    "a = individual_df.filter(items=models[0]['Ticker'])\n",
    "b = individual_df.filter(items=models[1]['Ticker'])\n",
    "c = individual_df.filter(items=models[2]['Ticker'])\n",
    "d = individual_df.filter(items=models[3]['Ticker'])\n",
    "e = individual_df.filter(items=models[4]['Ticker'])\n",
    "f = individual_df.filter(items=models[5]['Ticker'])\n",
    "g = individual_df.filter(items=models[6]['Ticker'])\n",
    "h = individual_df.filter(items=models[7]['Ticker'])\n",
    "i = individual_df.filter(items=models[8]['Ticker'])\n",
    "j = individual_df.filter(items=models[9]['Ticker'])\n",
    "\n",
    "dict = {\n",
    "    'NQ Conservative' : a,\n",
    "    'NQ Moderately Conservative' : b,\n",
    "    'NQ Moderate' : c,\n",
    "    'NQ Moderately Aggressive' : d,\n",
    "    'NQ Aggressive' : e,\n",
    "    'Q Conservative' : f,\n",
    "    'Q Moderately Conservative' : g,\n",
    "    'Q Moderate' : h,\n",
    "    'Q Moderately Aggressive' :  i,\n",
    "    'Q Aggressive' : j\n",
    "}\n",
    "\n",
    "# -----------------------------------------------\n",
    "\n",
    "external_stylesheets = [\n",
    "    {\n",
    "        \"href\": \"https://fonts.googleapis.com/css2?\"\n",
    "                \"family=Lato:wght@400;700&display=swap\",\n",
    "        \"rel\": \"stylesheet\",\n",
    "    },\n",
    "]\n",
    "\n",
    "# -----------------------------------------------\n",
    "\n",
    "# Build App\n",
    "app = dash.Dash(__name__, external_stylesheets=external_stylesheets)\n",
    "server = app.server\n",
    "app.title = \"sababa_portfolio_performance\"\n",
    "\n",
    "# ----------------------------------------------\n",
    "\n",
    "# App Layout\n",
    "\n",
    "app.layout = html.Div(\n",
    "    children=[\n",
    "        html.Div(\n",
    "            children=[\n",
    "       \n",
    "        # header         \n",
    "                html.P(children=\"📈\", className=\"header-emoji\"),\n",
    "                html.H1(\n",
    "                    children=\"Portfolio Performance\", className=\"header-title\"\n",
    "                ),\n",
    "                html.P(\n",
    "                    children=\"Analyze the performance of portfolio models\"\n",
    "                    \" and their individual components against a weighted\"\n",
    "                    \" benchmark and the S&P500 since implementation date\",\n",
    "                    className=\"header-description\",\n",
    "                ),\n",
    "            ],\n",
    "            className=\"header\",\n",
    "        ),\n",
    "\n",
    "        # dropdown menu\n",
    "        html.Div([\n",
    "        dcc.Dropdown(\n",
    "        id='model_dropdown',\n",
    "        options=[\n",
    "            {'label': 'NQ Conservative', 'value': 'NQ Conservative'},\n",
    "            {'label': 'NQ Moderately Conservative', 'value': 'NQ Moderately Conservative'},\n",
    "            {'label': 'NQ Moderate', 'value': 'NQ Moderate'},\n",
    "            {'label': 'NQ Moderately Aggressive', 'value': 'NQ Moderately Aggressive'},\n",
    "            {'label': 'NQ Aggressive', 'value': 'NQ Aggressive'},\n",
    "            {'label': 'Q Conservative', 'value': 'Q Conservative'},\n",
    "            {'label': 'Q Moderately Conservative', 'value': 'Q Moderately Conservative'},\n",
    "            {'label': 'Q Moderate', 'value': 'Q Moderate'},\n",
    "            {'label': 'Q Moderately Aggressive', 'value': 'Q Moderately Aggressive'},\n",
    "            {'label': 'Q Aggressive', 'value': 'Q Aggressive'}\n",
    "        ],\n",
    "        value='NQ Moderate',\n",
    "        className='container',\n",
    "        ),\n",
    "        html.Div(id='dd-output-container')\n",
    "]),\n",
    " \n",
    "        # graphs\n",
    "        dcc.Graph(\n",
    "            id = 'portfolio_graph',\n",
    "            config={\"displayModeBar\": False},\n",
    "            className=\"card\"\n",
    "        ),\n",
    "        dcc.Graph(\n",
    "            id = 'individual_graph',\n",
    "            config={\"displayModeBar\": False},\n",
    "            className=\"card\"\n",
    "        ),\n",
    "    ]\n",
    ")\n",
    "\n",
    "# ---------------------------------------------------------\n",
    "\n",
    "# portfolio graph\n",
    "\n",
    "@app.callback(\n",
    "    Output(component_id = 'portfolio_graph', component_property='figure'),\n",
    "    [Input(component_id = 'model_dropdown', component_property='value')]\n",
    ")\n",
    "\n",
    "\n",
    "def update_portfolio_graph(column_chosen):\n",
    "    dff = master_df\n",
    "    dfg = bench_df\n",
    "    dfh = sp_df\n",
    "\n",
    "    # create a graph of portfolio performance\n",
    "    fig=px.line()\n",
    "    fig.add_scatter(x = dff.index, y = dff[column_chosen], mode = 'lines', name = \"Portfolio\",)\n",
    "    fig.add_scatter(x = dff.index, y = dfg[column_chosen], mode = 'lines', name = \"Benchmark\")\n",
    "    fig.add_scatter(x = dff.index, y = dfh['S&P 500'], mode = 'lines', name = \"S&P 500\")\n",
    "    fig.update_layout(\n",
    "        title={\n",
    "            'text': \"Portfolio Performance vs. Benchmark and S&P500, Cumulative Return on $1\",\n",
    "            'y' : 0.95,\n",
    "            'x' : 0.5,\n",
    "            'xanchor': 'center',\n",
    "            'yanchor': 'top'})\n",
    "    return fig    \n",
    "    \n",
    "# ---------------------------------------------------------\n",
    "\n",
    "# individual security graph\n",
    "\n",
    "@app.callback(\n",
    "    Output(component_id = 'individual_graph', component_property='figure'),\n",
    "    [Input(component_id = 'model_dropdown', component_property='value')]\n",
    ")\n",
    "\n",
    "def update_individual_graph(column_chosen):\n",
    "    fig2 = px.line(dict[column_chosen], labels={\n",
    "                 \"value\" : \"Cumulative Return on $1\",\n",
    "                 \"variable\" : \"Security\"})\n",
    "    fig2.update_layout(\n",
    "        title={\n",
    "            'text': \"Individual Security Performance\",\n",
    "            'y' : 0.95,\n",
    "            'x' : 0.5,\n",
    "            'xanchor': 'center',\n",
    "            'yanchor': 'top'})\n",
    "    return fig2\n",
    "\n",
    "# ------------------------------------------------------\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    app.run_server(debug=True)\n",
    "    app.run_server(mode='jupyterlab')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7c09b2e5-2333-4927-b375-d71f2983507b",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import datetime
import calendar
import pathlib

Radio_items= dbc.Row(
    [
    dbc.RadioItems(
            options=[
                {"label": "Monthly Report", "value": 'Home'},
                {"label": "Compare Reports", "value": 'Compare'},
            ],
            value='Home',
            id="radioitems-input",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0 p-2",
    align="center",
)


navbar = dbc.Navbar(
    [html.A(
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row([dbc.Col(html.Img(src='assets/4u1.png', height="50px")),
                dbc.Col(dbc.NavbarBrand("4u ANALYSIS",style={'font-size':'170%'},className="ml-2")),
                ],
                align="center",no_gutters=True,
        ),href="http://127.0.0.1:8050/",
    ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(Radio_items, id="navbar-collapse", navbar=True),
    ],
color="dark",dark=True,
)

app = dash.Dash(external_stylesheets=[dbc.themes.SUPERHERO])
server=app.server

app.config['suppress_callback_exceptions'] = True

app.layout=html.Div([

            html.Div(navbar),

            html.Div(id='tab')
])

def cleaning_monthdf(dfm):

    ###CLEANING MONTHLY REPORT

    dfm.rename(columns=dfm.iloc[1], inplace=True)
    dfm.drop(index=[0, 1, 2], inplace=True)
    dfm.dropna(axis=1, inplace=True)
    dfm['DATE'] = dfm['DATE'].dt.strftime("%d")
    dfm['PROFIT_%'] = (dfm['AVERAGE'] / dfm['INCOME']) * 100
    return dfm


def stock_report(month,path):
    dfs = pd.read_csv(path+"S_"+month+".csv", index_col='SN.no')  # Stock Report
    ### CLEANING STOCK REPORT

    # Converting columns into proper format
    if dfs['PRICE'].dtype !="float":
        dfs['PRICE'] = dfs['PRICE'].astype(float)
        dfs['SOLDOUT'] = dfs['SOLDOUT'].astype(int)

    # Finding Numeric value of 'Code'
    if dfs['CODE'].dtype !="int64":
        c = "".split() #Before Running Enter the secret code
        n = np.arange(10)
        dc = dict(zip(c, n))

        def cnvcode(s):
            a = ""
            for i in s:
                a += str(dc.get(i))
            return int(a)

        dfs['CODE'] = dfs['CODE'].apply(cnvcode)
    if "PROFIT" not in dfs.columns:
        # Creating a Column as Profit

        def profit(a, b):
            return a - b

        dfs['PROFIT'] = profit(dfs['PRICE'], dfs['CODE'])

    ##PLOTTING FIGURE
    fig_stock = px.scatter(dfs[dfs['SOLDOUT'] > 0], x='PROFIT', y='SOLDOUT',
                           hover_name="ITEMS NAME", hover_data=['BARCODE', 'QUANTITY'])
    fig_stock.update_layout(title="Best Products")
    return fig_stock


def month_report(month,path):

    dfm = pd.read_excel(path+"M_"+month+".xlsx", sheet_name='Table 2')  # Monthly Report
    ###CLEANING MONTHLY REPORT

    dfm.rename(columns=dfm.iloc[1], inplace=True)
    dfm.drop(index=[0, 1, 2], inplace=True)
    dfm.dropna(axis=1, inplace=True)
    dfm['DATE'] = dfm['DATE'].dt.strftime("%d")
    dfm['PROFIT_%'] = (dfm['AVERAGE'] / dfm['INCOME']) * 100
    fig_month= px.bar(dfm, x=dfm['DATE'], y=dfm['PROFIT_%'], hover_data=['INCOME', 'AVERAGE'])
    fig_month.update_layout(title_text="Month : "+month.upper())
    return fig_month
    ## PLOTTING FIGURE

def pie_date(date,path):
    df2 = pd.read_excel(path+ str(date) + '.xlsx', sheet_name='Table 1')
    df2 = df2.rename(columns=df2.iloc[2]).drop(index=[0, 1, 2])
    fig_pie = go.Figure(data=[go.Pie(labels=["Profit", "Total"], values=[df2['Profit'].sum(), df2['Total'].sum()],
                                     pull=[0, 0.1])])
    fig_pie.update_layout(
        width=360,
        height=260,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=10,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig_pie

def pie(month,path):
    dfm = pd.read_excel(path+"M_" + month + ".xlsx", sheet_name='Table 2')  # Monthly Report
    dfm.rename(columns=dfm.iloc[1], inplace=True)
    dfm.drop(index=[0, 1, 2], inplace=True)
    dfm.dropna(axis=1, inplace=True)
    dfm['DATE'] = dfm['DATE'].dt.strftime("%d")
    # PIE CHARTS (Income vs Profit) ##
    fig_pie = go.Figure(data=[go.Pie(labels=["PROFIT", "INCOME"], values=[dfm['AVERAGE'].sum(), dfm['INCOME'].sum()],
                                     pull=[0, 0.1])])
    fig_pie.update_layout(
        width=360,
        height=260,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=10,
            pad=4
        ),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig_pie

def update_table(month,path):
    dfs = pd.read_csv(path+"S_"+month+".csv", index_col='SN.no')  # Stock Report
    df = dfs[dfs['QUANTITY'] < 5].sort_values(by=['SOLDOUT'], ascending=False).head(20)
    table=dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    return table

def update_info(month,path):
    dfm = pd.read_excel(path+"M_" + month + ".xlsx", sheet_name='Table 2')  # Monthly Report
    ###CLEANING MONTHLY REPORT

    dfm.rename(columns=dfm.iloc[1], inplace=True)
    dfm.drop(index=[0, 1, 2], inplace=True)
    dfm.dropna(axis=1, inplace=True)
    dfm['DATE'] = dfm['DATE'].dt.strftime("%d")
    dfm['PROFIT_%'] = (dfm['AVERAGE'] / dfm['INCOME']) * 100
    a="INCOME : Rs.{}".format("{:,}".format(int(dfm['INCOME'].sum())))
    b="PROFIT : Rs.{}".format("{:,}".format(int(dfm['AVERAGE'].sum())))

    return a,b

def update_graph_date(month,date,path):

    df2 = pd.read_excel(path+str(date)+'.xlsx', sheet_name='Table 1')

    df2 = df2.rename(columns=df2.iloc[2]).drop(index=[0, 1, 2])
    df2['PROFIT_%'] = (df2['Profit'] / df2['Total']) * 100

    fig3 = px.bar(df2, x=df2['Invoice no.'], y=df2['PROFIT_%'], hover_data=['Total', 'Profit', 'Discount'])
    fig3.update_layout(title_text="Month : "+month.upper()+" , Date : "+str(date))
    return fig3

def table_name(dfs,name):
    df=dfs[dfs['ITEMS NAME'].str.contains(name.upper())]
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    return table

def table_barcode(dfs,barcode):
    df=dfs[dfs['BARCODE']==barcode]
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    return table





pre_month=calendar.month_name[datetime.datetime.now().month-1]
year=datetime.datetime.now().year
card = dbc.Card(
    dbc.CardBody([
    html.Div([
        dbc.InputGroup([
                dbc.InputGroupAddon("YEAR", addon_type="append"),
                dbc.Input(id='selectyear',type="number",value="2020", min=2020, max=2030, step=1),
            ],className='col-6',id="style-numeric-input",),
        dbc.InputGroup([
                dbc.InputGroupAddon("DATE", addon_type="append"),
                dbc.Input(id='selectdate',type="number",value="", min=0, max=10, step=1),
            ],className='col-6',id="styled-numeric-input",),
    ],className='row'),

        dbc.InputGroup([
            dbc.InputGroupAddon("MONTH", addon_type="append"),
            dbc.Select(id="select",value=pre_month,options=[
                {"label":pre_month.upper(),"value":pre_month,"disabled": True},
                {"label": "JANUARY", "value": "january"},
                {"label": "FEBRUARY", "value": "february"},
                {"label": "MARCH", "value": "march"},
                {"label": "APRIL", "value": "april"},
                {"label": "MAY", "value": "may"},
                {"label": "JUNE", "value": "june"},
                {"label": "JULY", "value": "july"},
                {"label": "AUGUST", "value": "august"},
                {"label": "SEPTEMBER", "value": "september"},
                {"label": "OCTOBER", "value": "october"},
                {"label": "NOVEMBER", "value": "november"},
                {"label": "DECEMBER", "value": "december"},],),
        ],className="pt-2"),


        dcc.Graph(id='fig_pie',className="pt-2"),

        html.Div(id="inc",style={'color': 'blue', 'font-weight': 'bold', 'font-size': '120%'}),

        html.Div(id="pro",style={'color': 'red', 'font-weight': 'bold', 'font-size': '120%'}),

    ],className="pb-4"),

    style={"background": "orange"},
)


tab1=html.Div([
    html.Div([
            html.Div(card,className='col-4 p-3'),
            html.Div(dcc.Graph(id='fig_month'),className='col-8 pt-3'),
    ],className='row'),

    html.Div([
            html.Div([
                html.Div("STOCKS  (Needed products)",style={'font-size':'130%',"font-family": "Times New Roman, Times, serif"},className='d-flex justify-content-center pb-2'),
                html.Div(id='tab_stock'),
            ],className='col-5'),
            html.Div([
                    html.Div(dcc.Graph(id='fig_stockid')),

                    dbc.Label("SEARCH BY",style={'font-weight': 'bold', 'font-size': '120%',
                              "font-family": "Times New Roman, Times, serif"},
                    className='pt-3'),

                    html.Div([
                            dbc.InputGroup([
                                    dbc.InputGroupAddon("ITEMS NAME", addon_type="prepend"),
                                    dbc.Input(id='input',type='text',value="")],
                            className="col-7"),

                            dbc.InputGroup([
                                    dbc.InputGroupAddon("BARCODE", addon_type="prepend"),
                                    dbc.Input(id='items_barcode',type='number')],
                            className="col-5")
                    ],className='row'),

                    html.Div(id='tab_search',className="pb-2"),
            ],className='col-7'),

    ],className='row')
])

tab2=html.Div([
            html.Div([
                html.Div([
                html.Div("Select the Year",style={'font-weight': 'bold', 'font-size': '130%',
                              "font-family": "Times New Roman, Times, serif",'color':'orange'},className='ml-2'),

                html.Div(dbc.Input(id='comp_year',type="number", value=year,min=0, max=10, step=1),className='ml-2'),
                html.Div("Select the Months to Compare",style={'font-weight': 'bold', 'font-size': '130%',
                              "font-family": "Times New Roman, Times, serif",'color':'orange'},className='ml-2'),
                dcc.Dropdown(id="select_comp_month",
                             value=pre_month,
                             options=[
                                {"label":pre_month.upper(),"value":pre_month,"disabled": True},
                                {"label": "JANUARY", "value": "january"},
                                {"label": "FEBRUARY", "value": "february"},
                                {"label": "MARCH", "value": "march"},
                                {"label": "APRIL", "value": "april"},
                                {"label": "MAY", "value": "may"},
                                {"label": "JUNE", "value": "june"},
                                {"label": "JULY", "value": "july"},
                                {"label": "AUGUST", "value": "august"},
                                {"label": "SEPTEMBER", "value": "september"},
                                {"label": "OCTOBER", "value": "october"},
                                {"label": "NOVEMBER", "value": "november"},
                                {"label": "DECEMBER", "value": "december"}],
                             multi=True,style={'color':'black'},className="pt-2 pb-4")
                ],className='col-3'),
                dcc.Graph(id='line_graph',className='col-9',style={})

        ],className='row pt-4',style={'height':'80vh'}),
])



@app.callback(
    Output('tab','children'),
    [(Input('radioitems-input','value'))]
)
def update_tab(val):
    if val=='Home':
        return tab1
    else:
        return tab2

@app.callback(
    Output('line_graph','figure'),
    [Input('select_comp_month','value'),
     Input('comp_year','value')]
)
def update_comp(months,year):
    x_label=[]
    y_labelinc=[]
    y_labelpro=[]
    if type(months)!=str:
        for month in months:
            file=pathlib.Path(str(year)+'/'+month+'/'+ "M_" + month + ".xlsx")
            if file.exists():
                dfm = pd.read_excel(file, sheet_name='Table 2')  # Monthly Report
                df=cleaning_monthdf(dfm)
                x_label.append(month)
                y_labelpro.append(df['AVERAGE'].sum())
                y_labelinc.append(df['INCOME'].sum())

        fig = go.Figure(data=[
            go.Bar(name='Income', x=x_label, y=y_labelinc),
            go.Bar(name='Profit', x=x_label, y=y_labelpro)
        ])
        # Change the bar mode
        fig.update_layout(barmode='group',autosize=True,
                          xaxis_title="MONTHS",
                          yaxis_title="AMOUNT",
                          title="Comparing Months Reports",
                          title_font_family="Arial")

        return fig
    else:
        file = pathlib.Path(str(year) + '/' + months + '/' + "M_" + months + ".xlsx")
        if file.exists():
            dfm = pd.read_excel(file, sheet_name='Table 2')  # Monthly Report
            df = cleaning_monthdf(dfm)
            x_label.append(months)
            y_labelpro.append(df['AVERAGE'].sum())
            y_labelinc.append(df['INCOME'].sum())
            fig = go.Figure(data=[
                go.Bar(name='Income', x=x_label, y=y_labelinc),
                go.Bar(name='Profit', x=x_label, y=y_labelpro)
            ])
            # Change the bar mode
            fig.update_layout(barmode='group', autosize=True,
                              xaxis_title="MONTHS",
                              yaxis_title="AMOUNT",
                              title="Month : "+months,
                              title_font_family="Arial")
            return fig

@app.callback(
     Output('tab_search','children'),
     [(Input('select','value')),
      (Input('input','value')),
      (Input('items_barcode','value')),
        Input('selectyear','value')
     ]
)
def update(month,name,barcode,year):
    path=str(year)+'/'+month+'/'
    dfs = pd.read_csv(path+"S_" + month + ".csv", index_col='SN.no')  # Stock Report
    if name=="":
         a=table_barcode(dfs,barcode)
    else:
         a=table_name(dfs,name)
    return a

@app.callback(
    [Output('fig_stockid', 'figure'),
    Output('tab_stock', 'children'),
    Output('inc', 'children'),
    Output('pro', 'children'),],
    [Input('select', 'value'),
     Input('selectyear','value')])
def update_graph(month,year):
    path=str(year)+'/'+month+'/'
    c = stock_report(month,path)
    d = update_table(month,path)
    e,f = update_info(month,path)
    return c,d,e,f

@app.callback(
    [Output('fig_month','figure'),
    Output('fig_pie', 'figure')],
    [Input('select', 'value'),
     Input('selectdate','value'),
     Input('selectyear','value')]
)
def update_graph(month,date,year):
    path=str(year)+'/'+month+'/'
    file=pathlib.Path(path+str(date)+'.xlsx')
    if file.exists():
        a = update_graph_date(month,date,path)
        b = pie_date(date,path)
    else:
        a = month_report(month,path)
        b = pie(month,path)
    return a,b
if __name__=='__main__':
    app.run_server(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "wwe-tracker-421019-657b24ee796a.json", scope
)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
wrestlers_sheet = client.open("wwe-tracker").worksheet("wrestlers")

matches_sheet = client.open("wwe-tracker").worksheet("matches")

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Checklist(
        id='championship-filter',
        options=[{'label': 'Championship Filter', 'value': 'YES'}],
        value=[]
    ),
    html.Div(id='matches-output')
])

@app.callback(
    Output('matches-output', 'children'),
    [Input('championship-filter', 'value')]
)
def update_output(filter_value):
    if 'YES' in filter_value:
        matches = [match for match in matches if match['championship'] == 'yes']
    else:
        matches = matches_sheet.get_all_records()  # Retrieve the records once
    return html.Div([
        html.Div([
            html.Div(f"Matchseq: {match['matchseq']}", className='cell'),
            html.Div(f"Person: {match['person']}", className='cell'),
            # Add more fields here...
        ], className='row') for match in matches
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
from dash import Dash, dash_table, dcc, html, Input, Output, State, MATCH, ctx
from dash.dash_table import FormatTemplate
import dash_bootstrap_components as dbc
import pandas as pd
import openpyxl
import dash_auth


df = pd.read_excel("dashtestdata.xlsx")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

auth = dash_auth.BasicAuth(
    app,
    {'admin': 'alphega'}
)

options = [
    "Sehir",
    "Sube",
    "gln",
    "Firma"
]

def make_top10_dff(col):
    dff = df[[col, "Aktif / Cikis"]]
    dff = (
        dff.groupby(col)
        .sum()
        .sort_values(by="Aktif / Cikis", ascending=False)
        .head(10)
        .reset_index()
    )
    dff.loc["Total"] = dff.sum(numeric_only=True)
    return dff

def make_table(id, col):
    dff = make_top10_dff(col)
    return dash_table.DataTable(
        dff.to_dict("records"),
        [
            {"name": col, "id": col},
            {
                "name": "adet",
                "id": "Aktif / Cikis",
                "type": "numeric",
                # "format": FormatTemplate.money(2),
            },
        ],
        style_cell={"textAlign": "left"},
        style_cell_conditional=[
            {"if": {"column_id": "Aktif / Cikis"}, "textAlign": "right"}
        ],
        style_header={"backgroundColor": "white", "fontWeight": "bold"},
        style_as_list_view=True,
        id={"type": "top10-table", "index": id},
    )

def make_card(n_clicks, col):
    return dbc.Card(
        [
            dcc.Dropdown(
                options,
                col,
                id={"type": "top10-col", "index": n_clicks},
                clearable=False,
                className="my-4",
            ),
            make_table(n_clicks, col),
        ],
        style={"width": 500, "display": "inline-block"},
        className="m-3 px-2",
    )


app.layout = dbc.Container(
    [
        html.H3("Vitamin Grubu Satışlar Top 10 Listesi", className="ms-3"),
        dbc.Button("Liste Göster", id="top10-add-list", n_clicks=0, className="m-3"),
        dbc.Button("Temizle", id="top10-clear", className="m-3", outline=True, color="primary"),
        html.Div(id="top10-container", children=[], className="mt-3"),
    ],
    fluid=True,
)


@app.callback(
    Output("top10-container", "children"),
    Input("top10-add-list", "n_clicks"),
    Input("top10-clear", "n_clicks"),
    State("top10-container", "children"),
)
def add_top10_card(n_clicks, _, cards):
    if ctx.triggered_id == "top10-clear":
        return []
    new_card = make_card(n_clicks, options[0])
    cards.append(new_card)
    return cards


@app.callback(
    Output({"type": "top10-table", "index": MATCH}, "data"),
    Output({"type": "top10-table", "index": MATCH}, "columns"),
    Input({"type": "top10-col", "index": MATCH}, "value"),
)
def update_top10_data(col):
    data = make_top10_dff(col)
    cols = [
        {"name": "Top 10", "id": col},
        {
            "name": "adet",
            "id": "Aktif / Cikis",
            "type": "numeric",
            # "format": FormatTemplate.money(2),
        },
    ]
    return data.to_dict("records"), cols


if __name__ == "__main__":
    app.run_server(debug=False, port=8050)

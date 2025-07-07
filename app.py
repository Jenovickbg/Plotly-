

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import yfinance as yf
import plotly.express as px
import pandas as pd

# Initialiser l'application Dash
app = dash.Dash(__name__)
server = app.server  # Pour déploiement (Heroku, Vercel...)

# Liste des indices
indices = {
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq",
    "^GSPC": "S&P 500",
    "^FTSE": "FTSE 100",
    "^GDAXI": "DAX",
    "^FCHI": "CAC 40",
    "^N225": "Nikkei 225",
    "000001.SS": "Shanghai Composite",
    "^BSESN": "Sensex",
    "^STOXX50E": "Euro Stoxx 50"
}

# Layout de l'application
app.layout = html.Div([
    html.H1(" Dashboard Boursier Interactif", style={'textAlign': 'center'}),
    
    html.Label("Sélectionnez un indice boursier :"),
    dcc.Dropdown(
        id='indice-dropdown',
        options=[{'label': name, 'value': ticker} for ticker, name in indices.items()],
        value='^GSPC'
    ),
    
    html.Label("Sélectionnez la période d'analyse :"),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date='2020-01-01',
        end_date='2024-12-31'
    ),
    
    dcc.Graph(id='indice-graph'),
    
    html.Div(id='explication', style={'fontSize':20, 'marginTop':20})
])

# Callback pour mettre à jour le graphique et l'explication
@app.callback(
    [Output('indice-graph', 'figure'),
     Output('explication', 'children')],
    [Input('indice-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(ticker, start_date, end_date):
    try:
        # Télécharger les données
        df = yf.download(ticker, start=start_date, end=end_date, group_by='ticker')

        # Vérifier si df est vide
        if df.empty:
            fig = px.line(title=f" Aucune donnée pour {indices[ticker]}")
            explication = f" Aucune donnée n’a pu être récupérée pour **{indices[ticker]}** entre {start_date} et {end_date}."
            return fig, explication

        # Si MultiIndex (group_by='ticker' active)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(0)  # Enlève le premier niveau (ticker)

        # Vérifier la colonne 'Close'
        if "Close" not in df.columns:
            fig = px.line(title=f" Colonne 'Close' introuvable pour {indices[ticker]}")
            explication = f" La colonne **Close** est introuvable dans les données téléchargées."
            return fig, explication

        # Reset index et renommer la colonne Date
        df = df.reset_index()

        # Vérifier la longueur
        if len(df) < 2:
            fig = px.line(title=f" Pas assez de données pour {indices[ticker]}")
            explication = f" Il n’y a pas assez de données pour calculer la variation sur **{indices[ticker]}**."
            return fig, explication

        # Créer le graphique
        fig = px.line(df, x="Date", y="Close", title=f" Evolution de {indices[ticker]}")

        # Calculer la variation
        variation = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100

        # Générer l'explication
        if variation > 0:
            explication = f"L'indice **{indices[ticker]}** a augmenté de **{variation:.2f}%** durant cette période."
        else:
            explication = f"L'indice **{indices[ticker]}** a diminué de **{abs(variation):.2f}%** durant cette période."

        return fig, explication

    except Exception as e:
        # Gestion globale des erreurs
        fig = px.line(title=" Erreur lors du téléchargement ou traitement des données")
        explication = f" Une erreur est survenuee : **{str(e)}**"
        return fig, explication

    except Exception as e:
        # Gestion globale des erreurs
        fig = px.line(title=" Erreur lors du téléchargement ou traitement des données")
        explication = f" Une erreur est survenue : **{str(e)}**"
        return fig, explication



# Lancer le serveur
if __name__ == '__main__':
    app.run(debug=True)

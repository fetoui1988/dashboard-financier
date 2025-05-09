import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Configuration Streamlit
st.set_page_config(page_title="Dashboard Financier", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("Financial Data Clean.xlsx", sheet_name="Financials")
    df = df[df['Year'] != 2023]  # Supprimer 2023
    df["Q1"] = df[['Jan', 'Feb', 'Mar']].sum(axis=1)
    df["Q2"] = df[['Apr', 'May', 'Jun']].sum(axis=1)
    df["Q3"] = df[['Jul', 'Aug', 'Sep']].sum(axis=1)
    df["Q4"] = df[['Oct', 'Nov', 'Dec']].sum(axis=1)
    df["Total_Annuel"] = df[['Q1', 'Q2', 'Q3', 'Q4']].sum(axis=1)
    return df

df = load_data()

month_cols = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
quarter_cols = ['Q1', 'Q2', 'Q3', 'Q4']
base_cols = ['Account', 'Year', 'Scenario', 'business_unit', 'Currency']

# PAGE PRÉSENTATION
def page_presentation():
    st.title("📊 Projet - Dashboard Financier")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("sab.jpg", caption="Saber Fetoui", width=200)

    st.markdown("""
    ## Présentation
    Bienvenue sur ce tableau de bord financier réalisé avec **Python** et **Streamlit**.

    Ce projet a pour objectif de faciliter l'analyse de données financières par compte, unité d'affaires, trimestre et année. Il propose des visualisations interactives et des outils d'exploration.

    ### Fonctions principales
    - 📂 Visualisation des données originales et filtrées
    - 📈 Analyse de l'évolution annuelle des comptes
    - 💰 Suivi des marges bénéficiaires (trimestre et année)

    ### Réalisé par
    **ATEF FETOUI**  """)

# PAGE 1 : Données originales
def page_donnees_originales():
    st.title("📄 Données financières originales")
    afficher_mois = st.checkbox("Afficher les colonnes mensuelles", value=True)

    colonnes = base_cols + quarter_cols + ["Total_Annuel"]
    if afficher_mois:
        colonnes = base_cols + month_cols + quarter_cols + ["Total_Annuel"]

    df_affichage = df.copy()
    for col in month_cols + quarter_cols + ["Total_Annuel"]:
        df_affichage[col] = df_affichage[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else x)

    st.dataframe(df_affichage[colonnes])

# PAGE 2 : Données filtrées
def page_filtres():
    st.title("🎛 Données filtrées par compte, année et unité")

    annee = st.selectbox("📅 Année :", sorted(df['Year'].unique()))
    compte = st.selectbox("📂 Compte :", df['Account'].unique())
    unite = st.selectbox("🏢 Unité :", ["Toutes les unités"] + list(df['business_unit'].unique()))
    cacher_mois = st.checkbox("Cacher les colonnes mensuelles", value=True)

    colonnes = base_cols + quarter_cols + ["Total_Annuel"]
    if not cacher_mois:
        colonnes = base_cols + month_cols + quarter_cols + ["Total_Annuel"]

    if unite == "Toutes les unités":
        df_filtre = df[(df["Year"] == annee) & (df["Account"] == compte)].copy()
    else:
        df_filtre = df[(df["Year"] == annee) & (df["Account"] == compte) & (df["business_unit"] == unite)].copy()

    for col in month_cols + quarter_cols + ["Total_Annuel"]:
        df_filtre[col] = df_filtre[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else x)

    st.subheader(f"📋 Résultats : {compte} – {unite} – {annee}")
    st.dataframe(df_filtre[colonnes])

    st.markdown("**Totaux trimestriels :**")
    total_trim = df[(df["Year"] == annee) & (df["Account"] == compte)]
    if unite != "Toutes les unités":
        total_trim = total_trim[total_trim["business_unit"] == unite]
    resume_trim = total_trim[quarter_cols].sum().reset_index()
    resume_trim.columns = ["Trimestre", "Total"]
    resume_trim["Total"] = resume_trim["Total"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(resume_trim)

    st.markdown("**Total annuel :**")
    total_sum = total_trim["Total_Annuel"].sum()
    st.write(f"💰 **Total :** ${total_sum:,.2f}")

# PAGE 3 : Évolution annuelle
def page_evolution():
    st.title("📈 Évolution d’un compte par année")

    compte = st.selectbox("📂 Choisir un compte :", df['Account'].unique(), key="evo_compte")
    unite = st.selectbox("🏢 Filtrer par unité :", ["Toutes les unités"] + list(df['business_unit'].unique()), key="evo_unite")

    df_filtered = df[df["Account"] == compte].copy()
    if unite != "Toutes les unités":
        df_filtered = df_filtered[df_filtered["business_unit"] == unite]

    grouped = df_filtered.groupby("Year")["Total_Annuel"].sum().reset_index()

    st.subheader(f"📊 Évolution de {compte} ({unite})")

    fig, ax = plt.subplots(figsize=(9, 5))
    years = grouped['Year'].astype(str)
    values = grouped['Total_Annuel'] / 1_000_000  # en M$

    ax.bar(years, values, color='steelblue')
    ax.set_ylabel("Montant (en M$)")
    ax.set_title(f"Évolution annuelle de {compte}", fontsize=13)
    ax.ticklabel_format(style='plain', axis='y')
    ax.grid(axis='y', linestyle='--', alpha=0.4)

    st.pyplot(fig)

# PAGE 4 : Marges avec jauges
def page_marges():
    st.title("💸 Analyse des marges (trimestre + annuel)")

    comptes_revenus = ['Sales']
    comptes_couts = ['Cost of Goods Sold']

    df_revenus = df[df['Account'].isin(comptes_revenus)]
    df_couts = df[df['Account'].isin(comptes_couts)]

    annee = st.selectbox("📅 Choisissez l'année :", sorted(df['Year'].unique()), key="marge_year")

    revenus_annee = df_revenus[df_revenus['Year'] == annee]
    couts_annee = df_couts[df_couts['Year'] == annee]

    total_rev = revenus_annee['Total_Annuel'].sum()
    total_cout = couts_annee['Total_Annuel'].sum()

    if total_rev == 0:
        st.error("❌ Aucun revenu trouvé pour l’année sélectionnée. Vérifiez le compte 'Sales'.")
        st.write("📋 Comptes disponibles :", df['Account'].unique())
        return

    marges_trimestrielles = {}
    for trimestre in ['Q1', 'Q2', 'Q3', 'Q4']:
        rev = revenus_annee[trimestre].sum()
        cout = couts_annee[trimestre].sum()
        marge = ((rev - cout) / rev * 100) if rev != 0 else 0
        marges_trimestrielles[trimestre] = round(marge, 2)

    marge_annuelle = ((total_rev - total_cout) / total_rev * 100)

    st.subheader(f"📊 Marge bénéficiaire – {annee}")
    cols = st.columns(2)
    for i, trimestre in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=marges_trimestrielles[trimestre],
            number={'suffix': "%"},
            title={'text': f"{trimestre}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if marges_trimestrielles[trimestre] > 0 else "red"},
                'steps': [
                    {'range': [0, 20], 'color': "#ffcccc"},
                    {'range': [20, 50], 'color': "#ffe699"},
                    {'range': [50, 100], 'color': "#d9ead3"}
                ],
            }
        ))
        cols[i % 2].plotly_chart(fig, use_container_width=True)

    st.subheader("📘 Marge annuelle")
    fig_annee = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(marge_annuelle, 2),
        number={'suffix': "%"},
        title={'text': f"Année {annee}"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [0, 20], 'color': "#ffcccc"},
                {'range': [20, 50], 'color': "#ffe699"},
                {'range': [50, 100], 'color': "#d9ead3"}
            ],
        }
    ))
    st.plotly_chart(fig_annee, use_container_width=True)

# MENU
st.sidebar.title("📚 Menu")
page = st.sidebar.radio("Aller à :", [
    "Présentation",
    "Données originales",
    "Données filtrées",
    "Évolution par compte",
    "Analyse des marges"
])

if page == "Présentation":
    page_presentation()
elif page == "Données originales":
    page_donnees_originales()
elif page == "Données filtrées":
    page_filtres()
elif page == "Évolution par compte":
    page_evolution()
elif page == "Analyse des marges":
    page_marges()

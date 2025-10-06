import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    h1 {
        color: #00ff87;
        font-weight: 800;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    h2 {
        color: #667eea;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
    }
    h3 {
        color: #a78bfa;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.3);
    }
    .uploadedFile {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Fonction de nettoyage du dataframe
def clean_dataframe(df):
    """
    Nettoie et prépare le dataframe pour l'analyse
    """
    df_cleaned = df.copy()
    
    # Supprimer les lignes complètement vides
    df_cleaned = df_cleaned.dropna(how='all')
    
    # Supprimer les doublons
    df_cleaned = df_cleaned.drop_duplicates(subset=['Player'], keep='first')
    
    # Nettoyer la colonne Age
    if 'Age' in df_cleaned.columns:
        df_cleaned['Age'] = pd.to_numeric(df_cleaned['Age'], errors='coerce')
    
    # Colonnes numériques à nettoyer
    numeric_columns = ['MP', 'Starts', 'Min', '90s', 'Gls', 'Ast', 'G+A', 'G-PK', 
                      'PK', 'PKatt', 'CrdY', 'CrdR', 'xG', 'npxG', 'xAG', 'npxG+xAG',
                      'PrgC', 'PrgP', 'PrgR', 'Gls_90', 'Ast_90', 'G+A_90', 
                      'G-PK_90', 'G+A-PK_90', 'xG_90', 'xAG_90', 'xG+xAG_90', 
                      'npxG_90', 'npxG+xAG_90']
    
    for col in numeric_columns:
        if col in df_cleaned.columns:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
            # Remplacer les NaN par 0 pour les colonnes numériques
            df_cleaned[col] = df_cleaned[col].fillna(0)
    
    # Nettoyer les colonnes texte
    text_columns = ['Player', 'Nation', 'Pos', 'Squad', 'Comp']
    for col in text_columns:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].fillna('Unknown')
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
    
    # Supprimer les lignes sans nom de joueur
    if 'Player' in df_cleaned.columns:
        df_cleaned = df_cleaned[df_cleaned['Player'] != 'Unknown']
        df_cleaned = df_cleaned[df_cleaned['Player'] != '']
    
    return df_cleaned

# Fonction pour charger les données
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

# Titre principal
st.markdown("<h1>⚽ Football Analytics Dashboard</h1>", unsafe_allow_html=True)

# Sidebar pour l'upload et le nettoyage
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/football2--v1.png", width=100)
    st.markdown("## 📁 Chargement des données")
    
    # Upload du fichier
    uploaded_file = st.file_uploader(
        "Choisir un fichier CSV",
        type=["csv"],
        help="Assurez-vous que votre fichier contient toutes les colonnes requises"
    )
    
    st.markdown("---")
    
    # Variables pour stocker les données
    df = None
    df_cleaned = None
    
    if uploaded_file:
        try:
            # Chargement du fichier
            df = load_data(uploaded_file)
            
            # Afficher les infos du fichier original
            st.markdown("### 📊 Fichier Original")
            st.info(f"**Lignes:** {len(df)}\n\n**Colonnes:** {len(df.columns)}")
            
            # Nettoyage automatique
            with st.spinner("🧹 Nettoyage en cours..."):
                df_cleaned = clean_dataframe(df)
            
            st.success("✅ Nettoyage terminé!")
            
            # Afficher les infos après nettoyage
            st.markdown("### ✨ Fichier Nettoyé")
            rows_removed = len(df) - len(df_cleaned)
            st.metric("Lignes supprimées", rows_removed)
            st.metric("Lignes restantes", len(df_cleaned))
            
            # Bouton de téléchargement du fichier nettoyé
            csv_cleaned = df_cleaned.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Télécharger le CSV nettoyé",
                data=csv_cleaned,
                file_name="cleaned_players.csv",
                mime="text/csv",
                help="Téléchargez le fichier après nettoyage"
            )
            
            st.markdown("---")
            
            # Afficher les modifications effectuées
            with st.expander("🔍 Détails du nettoyage"):
                st.markdown(f"""
                - ✅ Doublons supprimés
                - ✅ Lignes vides supprimées
                - ✅ Valeurs manquantes traitées
                - ✅ Colonnes numériques converties
                - ✅ Textes nettoyés
                
                **Résultat:** {rows_removed} ligne(s) supprimée(s)
                """)
            
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement : {str(e)}")
            st.info("Vérifiez le format de votre fichier CSV")
    else:
        st.info("📤 Importez un fichier CSV pour commencer.")
    
    st.markdown("---")
    st.markdown("### 📊 À propos")
    st.info(
        "Ce dashboard permet d'analyser les performances "
        "des joueurs de football à travers différentes statistiques "
        "et visualisations interactives."
    )

# Vérification du fichier uploadé et nettoyé
if uploaded_file is not None and df_cleaned is not None:
    try:
        # Vérification des colonnes obligatoires
        required_columns = ['Rk','Player','Nation','Pos','Squad','Comp','Age','Born',
                          'MP','Starts','Min','90s','Gls','Ast','G+A','G-PK','PK',
                          'PKatt','CrdY','CrdR','xG','npxG','xAG','npxG+xAG',
                          'PrgC','PrgP','PrgR','Gls_90','Ast_90','G+A_90',
                          'G-PK_90','G+A-PK_90','xG_90','xAG_90','xG+xAG_90',
                          'npxG_90','npxG+xAG_90']
        
        missing_columns = [col for col in required_columns if col not in df_cleaned.columns]
        
        if missing_columns:
            st.error(f"❌ Colonnes manquantes : {', '.join(missing_columns)}")
        else:
            # Message de confirmation
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.success(f"✅ Données prêtes à l'analyse! ({len(df_cleaned)} joueurs)")
            
            # Utiliser df_cleaned pour toute l'analyse
            df = df_cleaned
            
            # Onglets principaux
            tab1, tab2 = st.tabs(["🌍 Vue Globale", "👤 Analyse Joueur"])
            
            # ============================================================
            # TAB 1: VUE GLOBALE
            # ============================================================
            with tab1:
                st.markdown("## 📊 Statistiques Globales")
                
                # KPIs principaux
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric(
                        "🎯 Total Joueurs",
                        f"{len(df):,}",
                        help="Nombre total de joueurs dans le dataset"
                    )
                
                with col2:
                    st.metric(
                        "⚽ Total Buts",
                        f"{df['Gls'].sum():,.0f}",
                        help="Somme de tous les buts marqués"
                    )
                
                with col3:
                    st.metric(
                        "🎯 Total Assists",
                        f"{df['Ast'].sum():,.0f}",
                        help="Somme de toutes les passes décisives"
                    )
                
                with col4:
                    st.metric(
                        "🏆 Championnats",
                        f"{df['Comp'].nunique()}",
                        help="Nombre de championnats différents"
                    )
                
                with col5:
                    st.metric(
                        "⏱️ Minutes jouées",
                        f"{df['Min'].sum():,.0f}",
                        help="Total des minutes jouées"
                    )
                
                st.markdown("---")
                
                # Graphiques en colonnes
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🏆 Top 10 Buteurs")
                    top_scorers = df.nlargest(10, 'Gls')[['Player', 'Gls', 'Squad', 'Comp']]
                    
                    fig_top_scorers = px.bar(
                        top_scorers,
                        x='Gls',
                        y='Player',
                        orientation='h',
                        color='Gls',
                        color_continuous_scale='Blues',
                        text='Gls',
                        hover_data=['Squad', 'Comp']
                    )
                    fig_top_scorers.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=False,
                        height=400
                    )
                    fig_top_scorers.update_traces(textposition='outside')
                    st.plotly_chart(fig_top_scorers, use_container_width=True)
                
                with col2:
                    st.markdown("### 🎯 Top 10 Passeurs")
                    top_assisters = df.nlargest(10, 'Ast')[['Player', 'Ast', 'Squad', 'Comp']]
                    
                    fig_top_assisters = px.bar(
                        top_assisters,
                        x='Ast',
                        y='Player',
                        orientation='h',
                        color='Ast',
                        color_continuous_scale='Greens',
                        text='Ast',
                        hover_data=['Squad', 'Comp']
                    )
                    fig_top_assisters.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=False,
                        height=400
                    )
                    fig_top_assisters.update_traces(textposition='outside')
                    st.plotly_chart(fig_top_assisters, use_container_width=True)
                
                st.markdown("---")
                
                # Analyses par championnat
                st.markdown("## 🏆 Analyse par Championnat")
                
                # Sélection du championnat
                competitions = ['Tous'] + sorted(df['Comp'].unique().tolist())
                selected_comp = st.selectbox("Sélectionnez un championnat", competitions)
                
                if selected_comp == 'Tous':
                    df_filtered = df
                else:
                    df_filtered = df[df['Comp'] == selected_comp]
                
                # Statistiques par championnat
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    comp_stats = df.groupby('Comp').agg({
                        'Gls': 'sum',
                        'Ast': 'sum',
                        'Player': 'count'
                    }).reset_index()
                    comp_stats.columns = ['Championnat', 'Buts', 'Assists', 'Joueurs']
                    
                    fig_comp_goals = px.bar(
                        comp_stats,
                        x='Championnat',
                        y='Buts',
                        color='Buts',
                        color_continuous_scale='Reds',
                        title='⚽ Buts par Championnat'
                    )
                    fig_comp_goals.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig_comp_goals, use_container_width=True)
                
                with col2:
                    fig_comp_assists = px.bar(
                        comp_stats,
                        x='Championnat',
                        y='Assists',
                        color='Assists',
                        color_continuous_scale='Purples',
                        title='🎯 Assists par Championnat'
                    )
                    fig_comp_assists.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig_comp_assists, use_container_width=True)
                
                with col3:
                    fig_comp_players = px.pie(
                        comp_stats,
                        values='Joueurs',
                        names='Championnat',
                        title='👥 Répartition des Joueurs',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    fig_comp_players.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white'
                    )
                    st.plotly_chart(fig_comp_players, use_container_width=True)
                
                st.markdown("---")
                
                # Analyse par position
                st.markdown("## 📍 Analyse par Position")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    pos_stats = df.groupby('Pos').agg({
                        'Gls': 'mean',
                        'Ast': 'mean',
                        'MP': 'mean',
                        'Player': 'count'
                    }).reset_index()
                    pos_stats.columns = ['Position', 'Buts Moy', 'Assists Moy', 'Matchs Moy', 'Nombre']
                    
                    fig_pos = px.scatter(
                        pos_stats,
                        x='Buts Moy',
                        y='Assists Moy',
                        size='Nombre',
                        color='Position',
                        text='Position',
                        title='⚽ Buts vs Assists par Position (moyenne)',
                        size_max=60
                    )
                    fig_pos.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        height=500
                    )
                    fig_pos.update_traces(textposition='top center')
                    st.plotly_chart(fig_pos, use_container_width=True)
                
                with col2:
                    fig_pos_bar = px.bar(
                        pos_stats.sort_values('Nombre', ascending=False),
                        x='Position',
                        y='Nombre',
                        color='Position',
                        title='👥 Nombre de Joueurs par Position',
                        text='Nombre'
                    )
                    fig_pos_bar.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=False,
                        height=500
                    )
                    st.plotly_chart(fig_pos_bar, use_container_width=True)
                
                st.markdown("---")
                
                # Distribution des performances
                st.markdown("## 📈 Distribution des Performances")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fig_goals_dist = px.histogram(
                        df_filtered,
                        x='Gls',
                        nbins=30,
                        title='Distribution des Buts',
                        color_discrete_sequence=['#667eea']
                    )
                    fig_goals_dist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig_goals_dist, use_container_width=True)
                
                with col2:
                    fig_assists_dist = px.histogram(
                        df_filtered,
                        x='Ast',
                        nbins=30,
                        title='Distribution des Assists',
                        color_discrete_sequence=['#764ba2']
                    )
                    fig_assists_dist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig_assists_dist, use_container_width=True)
                
                with col3:
                    fig_mp_dist = px.histogram(
                        df_filtered,
                        x='MP',
                        nbins=30,
                        title='Distribution des Matchs Joués',
                        color_discrete_sequence=['#f093fb']
                    )
                    fig_mp_dist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig_mp_dist, use_container_width=True)
                
                st.markdown("---")
                
                # Tableau récapitulatif
                st.markdown("## 📋 Données Détaillées")
                
                # Filtres
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pos_filter = st.multiselect(
                        "Filtrer par position",
                        options=sorted(df['Pos'].unique()),
                        default=[]
                    )
                
                with col2:
                    comp_filter = st.multiselect(
                        "Filtrer par championnat",
                        options=sorted(df['Comp'].unique()),
                        default=[]
                    )
                
                with col3:
                    min_goals = st.slider(
                        "Nombre minimum de buts",
                        min_value=0,
                        max_value=int(df['Gls'].max()),
                        value=0
                    )
                
                # Application des filtres
                df_table = df.copy()
                if pos_filter:
                    df_table = df_table[df_table['Pos'].isin(pos_filter)]
                if comp_filter:
                    df_table = df_table[df_table['Comp'].isin(comp_filter)]
                df_table = df_table[df_table['Gls'] >= min_goals]
                
                # Affichage du tableau
                display_columns = ['Player', 'Pos', 'Squad', 'Comp', 'Age', 'MP', 
                                 'Gls', 'Ast', 'G+A', 'xG', 'Min']
                st.dataframe(
                    df_table[display_columns].sort_values('Gls', ascending=False),
                    use_container_width=True,
                    height=400
                )
                
                # Téléchargement
                csv = df_table.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Télécharger les données filtrées",
                    data=csv,
                    file_name='filtered_players.csv',
                    mime='text/csv',
                )
            
            # ============================================================
            # TAB 2: ANALYSE JOUEUR
            # ============================================================
            with tab2:
                st.markdown("## 🔍 Recherche de Joueur")
                
                # Barre de recherche
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    search_term = st.text_input(
                        "🔎 Rechercher un joueur",
                        placeholder="Entrez le nom du joueur...",
                        help="Commencez à taper pour filtrer la liste"
                    )
                
                # Filtrage des joueurs
                if search_term:
                    filtered_players = df[df['Player'].str.contains(search_term, case=False, na=False)]
                    player_list = filtered_players['Player'].tolist()
                else:
                    player_list = df['Player'].tolist()
                
                with col2:
                    st.markdown("### ")
                    num_results = len(player_list)
                    st.info(f"📊 {num_results} résultat(s)")
                
                # Sélection du joueur
                if player_list:
                    selected_player = st.selectbox(
                        "Sélectionnez un joueur",
                        options=sorted(player_list),
                        help="Choisissez un joueur dans la liste"
                    )
                    
                    if selected_player:
                        player_data = df[df['Player'] == selected_player].iloc[0]
                        
                        st.markdown("---")
                        
                        # En-tête du joueur
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col1:
                            st.image("https://img.icons8.com/color/96/000000/user-male-circle--v1.png", width=120)
                        
                        with col2:
                            st.markdown(f"# {selected_player}")
                            st.markdown(f"### {player_data['Squad']} | {player_data['Comp']}")
                            st.markdown(f"**Position:** {player_data['Pos']} | **Âge:** {player_data['Age']} ans | **Nationalité:** {player_data['Nation']}")
                        
                        with col3:
                            st.metric("🏆 Niveau", f"MP: {int(player_data['MP'])}")
                        
                        st.markdown("---")
                        
                        # Métriques principales
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("⚽ Buts", int(player_data['Gls']))
                        
                        with col2:
                            st.metric("🎯 Assists", int(player_data['Ast']))
                        
                        with col3:
                            st.metric("🔥 G+A", int(player_data['G+A']))
                        
                        with col4:
                            st.metric("🎮 Matchs", int(player_data['MP']))
                        
                        with col5:
                            st.metric("⏱️ Minutes", int(player_data['Min']))
                        
                        st.markdown("---")
                        
                        # Graphiques de performance
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 📊 Performance vs Position")
                            
                            # Comparaison avec la moyenne de la position
                            same_position = df[df['Pos'] == player_data['Pos']]
                            
                            categories = ['Buts/90', 'Assists/90', 'xG/90', 'xAG/90', 'G+A/90']
                            
                            player_values = [
                                player_data['Gls_90'],
                                player_data['Ast_90'],
                                player_data['xG_90'],
                                player_data['xAG_90'],
                                player_data['G+A_90']
                            ]
                            
                            pos_avg = [
                                same_position['Gls_90'].mean(),
                                same_position['Ast_90'].mean(),
                                same_position['xG_90'].mean(),
                                same_position['xAG_90'].mean(),
                                same_position['G+A_90'].mean()
                            ]
                            
                            fig_radar = go.Figure()
                            
                            fig_radar.add_trace(go.Scatterpolar(
                                r=player_values,
                                theta=categories,
                                fill='toself',
                                name=selected_player,
                                line_color='#667eea'
                            ))
                            
                            fig_radar.add_trace(go.Scatterpolar(
                                r=pos_avg,
                                theta=categories,
                                fill='toself',
                                name=f'Moy. {player_data["Pos"]}',
                                line_color='#f093fb'
                            ))
                            
                            fig_radar.update_layout(
                                polar=dict(
                                    radialaxis=dict(
                                        visible=True,
                                        range=[0, max(max(player_values), max(pos_avg)) * 1.2]
                                    )),
                                showlegend=True,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white',
                                height=400
                            )
                            
                            st.plotly_chart(fig_radar, use_container_width=True)
                        
                        with col2:
                            st.markdown("### 🎯 Efficacité")
                            
                            # Graphique en barres comparatif
                            comparison_data = pd.DataFrame({
                                'Métrique': ['Buts', 'xG', 'Assists', 'xAG', 'G+A', 'xG+xAG'],
                                'Valeur': [
                                    player_data['Gls'],
                                    player_data['xG'],
                                    player_data['Ast'],
                                    player_data['xAG'],
                                    player_data['G+A'],
                                    player_data['xG']+player_data['xAG']
                                ]
                            })
                            
                            fig_efficiency = px.bar(
                                comparison_data,
                                x='Métrique',
                                y='Valeur',
                                color='Métrique',
                                text='Valeur',
                                title='Réalisé vs Attendu (xG/xAG)'
                            )
                            
                            fig_efficiency.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white',
                                showlegend=False,
                                height=400
                            )
                            
                            fig_efficiency.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                            
                            st.plotly_chart(fig_efficiency, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Comparaison avec la position
                        st.markdown(f"## 📊 Comparaison avec les autres {player_data['Pos']}")
                        
                        same_pos = df[df['Pos'] == player_data['Pos']].copy()
                        same_pos['is_selected'] = same_pos['Player'] == selected_player
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig_pos_gls = px.scatter(
                                same_pos,
                                x='MP',
                                y='Gls',
                                color='is_selected',
                                color_discrete_map={True: '#ff0000', False: '#667eea'},
                                size='Min',
                                hover_data=['Player', 'Squad'],
                                title=f'⚽ Buts en fonction de l\'expérience ({player_data["Pos"]})',
                                labels={'MP': 'Matchs Joués', 'Gls': 'Buts'}
                            )
                            
                            fig_pos_gls.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white',
                                showlegend=False,
                                height=400
                            )
                            
                            st.plotly_chart(fig_pos_gls, use_container_width=True)
                        
                        with col2:
                            fig_pos_ast = px.scatter(
                                same_pos,
                                x='MP',
                                y='Ast',
                                color='is_selected',
                                color_discrete_map={True: '#ff0000', False: '#764ba2'},
                                size='Min',
                                hover_data=['Player', 'Squad'],
                                title=f'🎯 Assists en fonction de l\'expérience ({player_data["Pos"]})',
                                labels={'MP': 'Matchs Joués', 'Ast': 'Assists'}
                            )
                            
                            fig_pos_ast.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white',
                                showlegend=False,
                                height=400
                            )
                            
                            st.plotly_chart(fig_pos_ast, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Classements
                        st.markdown("## 🏆 Classements")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            rank_gls = df.sort_values('Gls', ascending=False).reset_index(drop=True)
                            player_rank_gls = rank_gls[rank_gls['Player'] == selected_player].index[0] + 1
                            
                            st.metric(
                                "⚽ Classement Buts",
                                f"#{player_rank_gls}",
                                f"sur {len(df)} joueurs"
                            )
                        
                        with col2:
                            rank_ast = df.sort_values('Ast', ascending=False).reset_index(drop=True)
                            player_rank_ast = rank_ast[rank_ast['Player'] == selected_player].index[0] + 1
                            
                            st.metric(
                                "🎯 Classement Assists",
                                f"#{player_rank_ast}",
                                f"sur {len(df)} joueurs"
                            )
                        
                        with col3:
                            rank_ga = df.sort_values('G+A', ascending=False).reset_index(drop=True)
                            player_rank_ga = rank_ga[rank_ga['Player'] == selected_player].index[0] + 1
                            
                            st.metric(
                                "🔥 Classement G+A",
                                f"#{player_rank_ga}",
                                f"sur {len(df)} joueurs"
                            )
                        
                        st.markdown("---")
                        
                        # Statistiques détaillées
                        st.markdown("## 📋 Statistiques Détaillées")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### ⚽ Statistiques Offensives")
                            offensive_stats = {
                                'Buts': player_data['Gls'],
                                'Buts (hors penalty)': player_data['G-PK'],
                                'Penalties marqués': player_data['PK'],
                                'Penalties tentés': player_data['PKatt'],
                                'Assists': player_data['Ast'],
                                'Buts + Assists': player_data['G+A'],
                                'Expected Goals (xG)': player_data['xG'],
                                'Expected Assists (xAG)': player_data['xAG'],
                            }
                            
                            for stat, value in offensive_stats.items():
                                st.text(f"{stat}: {value:.2f}")
                        
                        with col2:
                            st.markdown("### 📊 Statistiques par 90 minutes")
                            per90_stats = {
                                'Buts/90': player_data['Gls_90'],
                                'Assists/90': player_data['Ast_90'],
                                'G+A/90': player_data['G+A_90'],
                                'xG/90': player_data['xG_90'],
                                'xAG/90': player_data['xAG_90'],
                                'xG+xAG/90': player_data['xG+xAG_90'],
                                'npxG/90': player_data['npxG_90'],
                                'npxG+xAG/90': player_data['npxG+xAG_90'],
                            }
                            
                            for stat, value in per90_stats.items():
                                st.text(f"{stat}: {value:.3f}")
                        
                        st.markdown("---")
                        
                        # Progression et discipline
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 🏃 Progression")
                            progression_stats = {
                                'Passes progressives (PrgP)': player_data['PrgP'],
                                'Courses progressives (PrgC)': player_data['PrgC'],
                                'Réceptions progressives (PrgR)': player_data['PrgR'],
                            }
                            
                            fig_prog = go.Figure(data=[
                                go.Bar(
                                    x=list(progression_stats.keys()),
                                    y=list(progression_stats.values()),
                                    marker_color=['#667eea', '#764ba2', '#f093fb'],
                                    text=list(progression_stats.values()),
                                    textposition='outside'
                                )
                            ])
                            
                            fig_prog.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white',
                                height=300,
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig_prog, use_container_width=True)
                        
                        with col2:
                            st.markdown("### 🟨🟥 Discipline")
                            
                            cards_data = pd.DataFrame({
                                'Type': ['Cartons Jaunes', 'Cartons Rouges'],
                                'Nombre': [player_data['CrdY'], player_data['CrdR']]
                            })
                            
                            fig_cards = px.bar(
                                cards_data,
                                x='Type',
                                y='Nombre',
                                color='Type',
                                color_discrete_map={
                                    'Cartons Jaunes': '#FFD700',
                                    'Cartons Rouges': '#FF0000'
                                },
                                text='Nombre'
                            )
                            
                            fig_cards.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white',
                                showlegend=False,
                                height=300
                            )
                            
                            fig_cards.update_traces(textposition='outside')
                            
                            st.plotly_chart(fig_cards, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Joueurs similaires
                        st.markdown("## 👥 Joueurs Similaires")
                        
                        # Calcul de similarité basé sur les stats normalisées
                        numeric_cols = ['Gls_90', 'Ast_90', 'xG_90', 'xAG_90', 'PrgC', 'PrgP']
                        
                        df_similar = df[df['Pos'] == player_data['Pos']].copy()
                        
                        for col in numeric_cols:
                            df_similar[f'{col}_norm'] = (df_similar[col] - df_similar[col].mean()) / df_similar[col].std()
                        
                        player_vector = player_data[[col for col in numeric_cols]].values
                        
                        similarities = []
                        for idx, row in df_similar.iterrows():
                            if row['Player'] != selected_player:
                                other_vector = row[[col for col in numeric_cols]].values
                                distance = np.linalg.norm(player_vector - other_vector)
                                similarities.append((row['Player'], row['Squad'], row['Comp'], distance))
                        
                        similarities.sort(key=lambda x: x[3])
                        top_similar = similarities[:5]
                        
                        similar_df = pd.DataFrame(top_similar, columns=['Joueur', 'Club', 'Championnat', 'Score de Similarité'])
                        similar_df['Score de Similarité'] = similar_df['Score de Similarité'].round(3)
                        
                        st.dataframe(similar_df, use_container_width=True, hide_index=True)
                        
                else:
                    st.warning("⚠️ Aucun joueur trouvé. Essayez une autre recherche.")
    
    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
        st.info("Vérifiez que votre fichier CSV contient toutes les colonnes requises et est correctement formaté.")

else:
    # Page d'accueil sans fichier
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2>👋 Bienvenue sur le Football Analytics Dashboard!</h2>
            <p style='font-size: 18px; color: #a78bfa;'>
                Uploadez un fichier CSV pour commencer l'analyse des données des joueurs.
            </p>
            <br>
            <p>📁 Utilisez le menu latéral pour charger votre fichier</p>
            <p>🧹 Le fichier sera automatiquement nettoyé après l'upload</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    with st.expander("📖 Instructions d'utilisation"):
        st.markdown("""
        ### Comment utiliser ce dashboard ?
        
        1. **Chargement des données** 📤
           - Cliquez sur "Browse files" dans la barre latérale
           - Sélectionnez votre fichier CSV contenant les données des joueurs
           - Le fichier sera automatiquement nettoyé (doublons, valeurs manquantes, etc.)
           - Téléchargez le fichier nettoyé si besoin
           
        2. **Vue Globale** 🌍
           - Visualisez les statistiques générales de tous les joueurs
           - Explorez les performances par championnat
           - Analysez les distributions par position
           
        3. **Analyse Joueur** 👤
           - Recherchez un joueur spécifique
           - Consultez ses statistiques détaillées
           - Comparez-le avec d'autres joueurs de la même position
           - Découvrez les joueurs similaires
        
        ### Colonnes requises dans le CSV :
        
        `Rk, Player, Nation, Pos, Squad, Comp, Age, Born, MP, Starts, Min, 90s, 
        Gls, Ast, G+A, G-PK, PK, PKatt, CrdY, CrdR, xG, npxG, xAG, npxG+xAG, 
        PrgC, PrgP, PrgR, Gls_90, Ast_90, G+A_90, G-PK_90, G+A-PK_90, xG_90, 
        xAG_90, xG+xAG_90, npxG_90, npxG+xAG_90`
        
        ### 🧹 Processus de nettoyage automatique :
        
        - ✅ Suppression des lignes vides
        - ✅ Suppression des doublons
        - ✅ Conversion des colonnes numériques
        - ✅ Traitement des valeurs manquantes
        - ✅ Nettoyage des données textuelles
        """)
    
    with st.expander("💡 Fonctionnalités principales"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 Visualisations
            - Graphiques interactifs avec Plotly
            - Tableaux de bord dynamiques
            - Comparaisons multi-critères
            - Radar charts pour performances
            """)
        
        with col2:
            st.markdown("""
            ### 🔍 Analyses
            - Statistiques globales et par championnat
            - Analyse par position de jeu
            - Comparaisons entre joueurs
            - Détection de joueurs similaires
            - Nettoyage automatique des données
            """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>⚽ Football Analytics Dashboard | Fait avec ❤️ en utilisant Streamlit et Plotly</p>
        <p>🧹 Inclut un système de nettoyage automatique des données</p>
    </div>
""", unsafe_allow_html=True)
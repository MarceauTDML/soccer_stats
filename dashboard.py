import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.verify_data import clean_dataframe
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# Configuration
st.set_page_config(page_title="Football Analytics Dashboard", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

# CSS optimisé
st.markdown("""<style>
.main{background-color:#0e1117}.stMetric{background-color:#1e2130;padding:15px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1)}
h1{color:#00ff87;font-weight:800;text-align:center;padding:20px;background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);border-radius:10px;margin-bottom:30px}
h2{color:#667eea;border-bottom:3px solid #667eea;padding-bottom:10px}h3{color:#a78bfa}
.stButton>button{background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);color:white;border-radius:20px;padding:10px 25px;font-weight:bold;border:none;box-shadow:0 4px 6px rgba(0,0,0,0.2)}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 6px 8px rgba(0,0,0,0.3)}
</style>""", unsafe_allow_html=True)

# Fonction pour créer des graphiques
def create_plot(data, chart_type, **kwargs):
    plot_config = {'plot_bgcolor':'rgba(0,0,0,0)', 'paper_bgcolor':'rgba(0,0,0,0)', 'font_color':'white', 'showlegend':False}
    fig = getattr(px, chart_type)(data, **kwargs)
    fig.update_layout(**plot_config)
    return fig

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/football2--v1.png", width=100)
    st.markdown("## 📁 Chargement des données")
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])
    
    df = None
    if uploaded_file:
        try:
            df_original = pd.read_csv(uploaded_file)
            st.markdown("### 📊 Fichier Original")
            st.info(f"**Lignes:** {len(df_original)}\n\n**Colonnes:** {len(df_original.columns)}")
            
            with st.spinner("🧹 Nettoyage en cours..."):
                df = clean_dataframe(df_original)
                for msg in (df.attrs.get("errors") or []):
                    st.warning(msg)
            
            st.success("✅ Nettoyage terminé!")
            
            st.markdown("### ✨ Fichier Nettoyé")
            rows_removed = len(df_original) - len(df)
            st.metric("Lignes supprimées", rows_removed)
            st.metric("Lignes restantes", len(df))
            
            st.download_button("📥 Télécharger le CSV nettoyé", df.to_csv(index=False).encode("utf-8"), 
                             "cleaned_players.csv", "text/csv")
            
            st.markdown("---")
            
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
            st.error(f"❌ Erreur : {str(e)}")
            df = None
    else:
        st.info("📤 Importez un fichier CSV pour commencer.")
    
    st.markdown("---\n### 📊 À propos")
    st.info("Dashboard d'analyse des performances des joueurs de football.")

# Main content
if df is not None and len(df) > 0:
    try:
        # Message temporaire au lieu de la barre verte persistante
        st.toast(f"✅ {len(df)} joueurs chargés avec succès!", icon="⚽")
        
        tab1, tab2 = st.tabs(["🌍 Vue Globale", "👤 Analyse Joueur"])
        
        with tab1:
            # TOP 10 BUTEURS
            st.markdown("### ⚽ Top 10 Buteurs")
            top_scorers = df.nlargest(10, 'Gls')[['Player','Gls','Squad','Comp']]
            fig_scorers = create_plot(top_scorers, 'bar', x='Gls', y='Player', orientation='h', color='Gls', 
                             color_continuous_scale='Reds', text='Gls', hover_data=['Squad','Comp'])
            fig_scorers.update_traces(textposition='outside')
            fig_scorers.update_layout(height=400)
            st.plotly_chart(fig_scorers, use_container_width=True)
            
            st.markdown("---")
            
            # TOP 10 PASSEURS
            st.markdown("### 🎯 Top 10 Passeurs")
            top_assist = df.nlargest(10, 'Ast')[['Player','Ast','Squad','Comp']]
            fig_assist = create_plot(top_assist, 'bar', x='Ast', y='Player', orientation='h', color='Ast', 
                             color_continuous_scale='Greens', text='Ast', hover_data=['Squad','Comp'])
            fig_assist.update_traces(textposition='outside')
            fig_assist.update_layout(height=400)
            st.plotly_chart(fig_assist, use_container_width=True)
            
            # Analyse par championnat
            st.markdown("---\n## 🏆 Analyse par Championnat")
            competitions = ['Tous'] + sorted(df['Comp'].unique().tolist())
            selected_comp = st.selectbox("Sélectionnez un championnat", competitions)
            df_filtered = df if selected_comp == 'Tous' else df[df['Comp'] == selected_comp]
            
            # Distributions
            col1, col2, col3 = st.columns(3)
            charts = [
                (col1, 'Gls', 'Buts', '#667eea'),
                (col2, 'Ast', 'Assists', '#764ba2'),
                (col3, 'MP', 'Matchs Joués', '#f093fb')
            ]
            
            for col, field, title, color in charts:
                with col:
                    fig = create_plot(df_filtered, 'histogram', x=field, nbins=30, 
                                     title=f'Distribution des {title}', 
                                     color_discrete_sequence=[color])
                    st.plotly_chart(fig, use_container_width=True)
            
            # Tableau filtrable
            st.markdown("---\n## 📊 Tableau des Joueurs")
            col1, col2, col3 = st.columns(3)
            with col1:
                pos_filter = st.multiselect("Position", df['Pos'].unique())
            with col2:
                comp_filter = st.multiselect("Championnat", df['Comp'].unique())
            with col3:
                min_goals = st.slider("Buts minimum", 0, int(df['Gls'].max()), 0)
            
            df_table = df.copy()
            if pos_filter:
                df_table = df_table[df_table['Pos'].isin(pos_filter)]
            if comp_filter:
                df_table = df_table[df_table['Comp'].isin(comp_filter)]
            df_table = df_table[df_table['Gls'] >= min_goals]
            
            display_cols = ['Player','Pos','Squad','Comp','Age','MP','Gls','Ast','G+A','xG','Min']
            st.dataframe(df_table[display_cols].sort_values('Gls', ascending=False), use_container_width=True, height=400)
            st.download_button("📥 Télécharger les données filtrées", df_table.to_csv(index=False).encode('utf-8'), 
                              'filtered_players.csv', 'text/csv')
        
        with tab2:
            st.markdown("## 🔍 Recherche de Joueur")
            col1, col2 = st.columns([3,1])
            
            with col1:
                search_term = st.text_input("🔎 Rechercher un joueur", placeholder="Entrez le nom...", key="search")
            
            if search_term:
                player_list = df[df['Player'].str.contains(search_term, case=False, na=False)]['Player'].tolist()
            else:
                player_list = df['Player'].tolist()
            
            with col2:
                st.markdown("### ")
                st.info(f"📊 {len(player_list)} résultat(s)")
            
            if player_list:
                selected_player = st.selectbox("Sélectionnez un joueur", sorted(player_list))
                
                if selected_player:
                    p = df[df['Player'] == selected_player].iloc[0]
                    
                    st.markdown(f"---\n## 👤 {selected_player}")
                    
                    # Métriques principales
                    cols = st.columns(4)
                    metrics = [
                        ('🏟️ Club', p['Squad']),
                        ('🏆 Championnat', p['Comp']),
                        ('📍 Position', p['Pos']),
                        ('🎂 Âge', int(p['Age']))
                    ]
                    for col, (label, value) in zip(cols, metrics):
                        col.metric(label, value)
                    
                    st.markdown("---")
                    
                    # Stats clés
                    cols = st.columns(4)
                    stats = [
                        ('⚽ Buts', int(p['Gls'])),
                        ('🎯 Assists', int(p['Ast'])),
                        ('🎮 Matchs Joués', int(p['MP'])),
                        ('⏱️ Minutes', int(p['Min']))
                    ]
                    for col, (label, value) in zip(cols, stats):
                        col.metric(label, value)
                    
                    st.markdown("---")
                    
                    # Expected stats et Progression
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### ⚽ Statistiques Offensives")
                        offensive = {
                            'Buts': p['Gls'],
                            'Assists': p['Ast'],
                            'Buts + Assists': p['G+A'],
                            'Buts hors penalty': p['G-PK'],
                            'Penaltys marqués': p['PK'],
                            'Penaltys tentés': p['PKatt'],
                            'Expected Goals (xG)': p['xG'],
                            'npxG': p['npxG'],
                            'xAG': p['xAG'],
                            'npxG+xAG': p['npxG+xAG']
                        }
                        for stat, value in offensive.items():
                            st.text(f"{stat}: {value:.2f}" if isinstance(value, float) else f"{stat}: {int(value)}")
                    
                    with col2:
                        st.markdown("### 🏃 Progression")
                        progression = {
                            'Passes progressives (PrgP)': p['PrgP'],
                            'Courses progressives (PrgC)': p['PrgC'],
                            'Réceptions progressives (PrgR)': p['PrgR']
                        }
                        for stat, value in progression.items():
                            st.text(f"{stat}: {value:.0f}")
                    
                    # Cartons
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 🟨🟥 Discipline")
                        cards_df = pd.DataFrame({
                            'Type': ['Cartons Jaunes', 'Cartons Rouges'], 
                            'Nombre': [int(p['CrdY']), int(p['CrdR'])]
                        })
                        fig = px.bar(cards_df, x='Type', y='Nombre', color='Type', 
                                    color_discrete_map={'Cartons Jaunes':'#FFD700', 'Cartons Rouges':'#FF0000'}, 
                                    text='Nombre')
                        fig.update_traces(textposition='outside')
                        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                         font_color='white', showlegend=False, height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("### 📊 Minutes jouées")
                        mins_data = pd.DataFrame({
                            'Catégorie': ['Minutes totales', 'Matchs démarrés', 'Matchs joués'],
                            'Valeur': [int(p['Min']), int(p['Starts']), int(p['MP'])]
                        })
                        fig = px.bar(mins_data, x='Catégorie', y='Valeur', color='Catégorie',
                                    color_discrete_sequence=['#667eea', '#764ba2', '#f093fb'], text='Valeur')
                        fig.update_traces(textposition='outside')
                        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                         font_color='white', showlegend=False, height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Radar chart et Stats /90
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 📈 Radar des Performances")
                        same_pos = df[df['Pos'] == p['Pos']]
                        categories = ['Buts/90', 'Assists/90', 'xG/90', 'xAG/90', 'G+A/90']
                        player_vals = [p['Gls_90'], p['Ast_90'], p['xG_90'], p['xAG_90'], p['G+A_90']]
                        pos_avg = [same_pos['Gls_90'].mean(), same_pos['Ast_90'].mean(), 
                                  same_pos['xG_90'].mean(), same_pos['xAG_90'].mean(), same_pos['G+A_90'].mean()]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(r=player_vals, theta=categories, fill='toself', 
                                                      name=selected_player, line_color='#667eea'))
                        fig.add_trace(go.Scatterpolar(r=pos_avg, theta=categories, fill='toself', 
                                                      name=f'Moy. {p["Pos"]}', line_color='#f093fb'))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, max(max(player_vals), max(pos_avg))*1.1])),
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                            font_color='white', height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("### ⚖️ Stats /90 min")
                        stats_90 = {
                            'Buts': p['Gls_90'],
                            'Assists': p['Ast_90'],
                            'G+A': p['G+A_90'],
                            'xG': p['xG_90'],
                            'xAG': p['xAG_90']
                        }
                        stats_df = pd.DataFrame(list(stats_90.items()), columns=['Stat', 'Valeur'])
                        fig = px.bar(stats_df, x='Stat', y='Valeur', color='Valeur', 
                                    color_continuous_scale='Purples', text='Valeur')
                        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                         font_color='white', showlegend=False, height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparaison position
                    st.markdown("---\n### 🎯 Comparaison par Position")
                    same_pos_comp = same_pos.copy()
                    same_pos_comp['is_selected'] = same_pos_comp['Player'] == selected_player
                    fig = px.scatter(same_pos_comp, x='Gls_90', y='Ast_90', size='G+A', color='is_selected',
                                    color_discrete_map={True:'#00ff87', False:'#667eea'}, 
                                    hover_data=['Player', 'Squad'],
                                    title=f'Comparaison des {p["Pos"]} (Buts/90 vs Assists/90)')
                    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                     font_color='white', showlegend=False, height=500)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Classements
                    st.markdown("---")
                    cols = st.columns(3)
                    rankings = [
                        ('Gls', '⚽ Classement Buts'),
                        ('Ast', '🎯 Classement Assists'),
                        ('G+A', '🔥 Classement G+A')
                    ]
                    for col, (field, label) in zip(cols, rankings):
                        rank = df.sort_values(field, ascending=False).reset_index(drop=True)
                        player_rank = rank[rank['Player'] == selected_player].index[0] + 1
                        col.metric(label, f"#{player_rank}/{len(df)}")
                    
                    # Joueurs similaires
                    st.markdown("---\n## 🔍 Joueurs Similaires")
                    same_pos_sim = df[(df['Pos'] == p['Pos']) & (df['Player'] != selected_player)].copy()
                    
                    if len(same_pos_sim) > 0:
                        features = ['Gls_90', 'Ast_90', 'xG_90', 'xAG_90']
                        
                        scaler = StandardScaler()
                        scaled = scaler.fit_transform(same_pos_sim[features])
                        player_feat = scaler.transform([[p[f] for f in features]])
                        similarities = cosine_similarity(player_feat, scaled)[0]
                        
                        same_pos_sim['similarity'] = similarities
                        similar = same_pos_sim.nlargest(min(5, len(same_pos_sim)), 'similarity')[['Player', 'Squad', 'Comp', 'similarity']]
                        similar.columns = ['Joueur', 'Club', 'Championnat', 'Score de Similarité']
                        similar['Score de Similarité'] = similar['Score de Similarité'].round(3)
                        st.dataframe(similar, use_container_width=True, hide_index=True)
                    else:
                        st.info("Aucun joueur similaire trouvé à cette position.")
            else:
                st.warning("⚠️ Aucun joueur trouvé.")
    
    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
        st.info("Vérifiez que votre fichier CSV contient toutes les colonnes requises.")

else:
    st.markdown("""<div style='text-align:center;padding:50px'>
    <h2>👋 Bienvenue sur le Football Analytics Dashboard!</h2>
    <p style='font-size:18px;color:#a78bfa'>Uploadez un fichier CSV pour commencer l'analyse.</p>
    <br><p>📁 Utilisez le menu latéral pour charger votre fichier</p>
    <p>🧹 Le fichier sera automatiquement nettoyé après l'upload</p></div>""", unsafe_allow_html=True)
    
    with st.expander("📖 Instructions d'utilisation"):
        st.markdown("""
        ### Comment utiliser ce dashboard ?
        
        1. **Chargement des données** 📤
           - Cliquez sur "Browse files" dans la barre latérale
           - Sélectionnez votre fichier CSV
           - Le fichier sera automatiquement nettoyé
           
        2. **Vue Globale** 🌍
           - Top 10 buteurs et passeurs
           - Statistiques par championnat
           - Distributions des performances
           
        3. **Analyse Joueur** 👤
           - Recherchez un joueur spécifique
           - Consultez ses statistiques détaillées
           - Comparez-le avec d'autres joueurs
        
        ### Colonnes requises dans le CSV :
        
        `Rk, Player, Nation, Pos, Squad, Comp, Age, Born, MP, Starts, Min, 90s, 
        Gls, Ast, G+A, G-PK, PK, PKatt, CrdY, CrdR, xG, npxG, xAG, npxG+xAG, 
        PrgC, PrgP, PrgR, Gls_90, Ast_90, G+A_90, G-PK_90, G+A-PK_90, xG_90, 
        xAG_90, xG+xAG_90, npxG_90, npxG+xAG_90`
        """)
    
    with st.expander("💡 Fonctionnalités principales"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 Visualisations
            - Graphiques interactifs
            - Top 10 buteurs et passeurs
            - Tableaux de bord dynamiques
            - Radar charts pour performances
            """)
        
        with col2:
            st.markdown("""
            ### 🔍 Analyses
            - Statistiques globales et par championnat
            - Analyse par position
            - Comparaisons entre joueurs
            - Détection de joueurs similaires
            - Nettoyage automatique
            """)

st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;padding:20px'><p>⚽ Football Analytics Dashboard | Fait avec ❤️ en utilisant Streamlit et Plotly</p><p>🧹 Inclut un système de nettoyage automatique des données</p></div>", unsafe_allow_html=True)

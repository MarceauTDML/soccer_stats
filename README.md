# Soccer Stats
Datavisualisation interactive des performances de joueurs évoluant dans les 5 grands championnats.

---

## L’application Streamlit permet :
- le nettoyage du CSV upload sur le dashboard
- une gestion basique des erreurs
- une vue globale par championnat
- une analyse individuelle par joueur

---

## Réutiliser le projet

### 1. Cloner le projet
```git clone <ton-repo>.git```

```cd <ton-repo>```

### 2. Créer un environnement virtuel
```python -m venv .venv```
- macOS/Linux
```source .venv/bin/activate```
- Windows
```.\.venv\Scripts\Activate```

### 3. Installer les dépendances
```pip install -r requirements.txt```

### 4. Lancer le dashboard
```streamlit run dashboard.py```

---

## Le fichier CSV
- Fichier CSV contenant les stats des joueurs.

- Colonnes attendues :
```Rk,Player,Nation,Pos,Squad,Comp,Age,Born,MP,Starts,Min,90s,Gls,Ast,G+A,G-PK,PK,PKatt,CrdY,CrdR,xG,npxG,xAG,npxG+xAG,PrgC,PrgP,PrgR,Gls_90,Ast_90,G+A_90,G-PK_90,G+A-PK_90,xG_90,xAG_90,xG+xAG_90,npxG_90,npxG+xAG_90```

---
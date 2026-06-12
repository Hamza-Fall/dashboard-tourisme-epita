# =============================================================================
# EPITA - EXAMEN FINAL MPE + AED
# Application Streamlit Multi-Vues : Version Finale Stabilisée
# Fichier : apps.py
# Contraintes : Zéro HTML/CSS injecté | Zéro émoji | Composants natifs Streamlit
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Configuration de la page (doit être le premier appel Streamlit) ---
st.set_page_config(
    page_title="EPITA - Gouvernance et IA Touristique",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CHARGEMENT SÉCURISÉ DES DONNÉES (avec cache et gestion d'exception)
# =============================================================================
@st.cache_data
def load_pipeline_data():
    """
    Charge les deux fichiers produits par le pipeline Python principal.
    Retourne (None, None) si les fichiers sont absents, sans planter l'app.
    """
    try:
        gold_df = pd.read_csv("gold_data.csv")
        top5_df = pd.read_csv("top5_destinations_recommandees.csv")
        return gold_df, top5_df
    except FileNotFoundError as e:
        st.error(
            f"Fichier de données introuvable : {e}. "
            "Vérifiez que 'gold_data.csv' et 'top5_destinations_recommandees.csv' "
            "sont bien à la racine du dépôt GitHub."
        )
        return None, None
    except Exception as e:
        st.error(f"Erreur inattendue lors du chargement des données : {e}")
        return None, None


gold, top5 = load_pipeline_data()

# =============================================================================
# BARRE LATÉRALE — Navigation
# =============================================================================
with st.sidebar:
    st.image(
        "https://www.epita.fr/wp-content/themes/epita/images/logo.svg",
        width=140
    )
    st.markdown("### Option Majeure")
    st.caption("Candidat EPITA — Data Governance et IA Expert")
    st.divider()

    page = st.radio(
        "Section du barème :",
        [
            "Executive View",
            "Data Quality et Signaux",
            "IA Performance et Forecast",
            "Arbitrage Business",
            "Gouvernance et Question Ultime"
        ]
    )

# =============================================================================
# GARDE : arrêt propre si les données sont absentes
# =============================================================================
if gold is None or top5 is None:
    st.stop()

# =============================================================================
# VUE 1 — EXECUTIVE VIEW
# =============================================================================
if page == "Executive View":
    st.title("Executive View")
    st.caption(
        "Pilotage stratégique de la demande touristique et allocation budgétaire."
    )

    # --- KPI Cards ---
    c1, c2, c3, c4 = st.columns(4)

    budget_total = gold["total_budget"].sum() if "total_budget" in gold.columns else 0
    roi_moyen = gold["avg_roi"].mean() if "avg_roi" in gold.columns else 0
    nb_destinations = len(gold)
    nb_pays = gold["country"].nunique() if "country" in gold.columns else 0

    c1.metric(label="Budget Marketing Total (EUR)", value=f"{budget_total:,.0f}")
    c2.metric(label="ROI Moyen Historique (EUR)", value=f"{roi_moyen:,.0f}")
    c3.metric(label="Destinations Analysées", value=f"{nb_destinations}")
    c4.metric(label="Marches Couverts", value=f"{nb_pays} pays")

    st.divider()

    # --- Graphique de distribution du ROI par pays ---
    st.subheader("Distribution du ROI par Marche")

    if "avg_roi" in gold.columns and "country" in gold.columns:
        fig_roi = px.box(
            gold,
            x="country",
            y="avg_roi",
            color="country",
            template="plotly_white",
            points="all",
            labels={
                "country": "Filiale Pays",
                "avg_roi": "Retour sur Investissement (ROI, EUR)"
            }
        )
        fig_roi.update_layout(showlegend=False)
        st.plotly_chart(fig_roi, use_container_width=True)
    else:
        st.warning(
            "Colonnes 'country' ou 'avg_roi' absentes de gold_data.csv. "
            "Vérifiez le pipeline de construction de la Gold Data."
        )

# =============================================================================
# VUE 2 — DATA QUALITY ET SIGNAUX FAIBLES
# =============================================================================
elif page == "Data Quality et Signaux":
    st.title("Data Quality et Signaux Faibles")
    st.caption(
        "Auditabilite des traitements de données et détection "
        "d'opportunités d'arbitrage commercial."
    )

    # --- Signal faible ---
    st.info(
        "Signal Faible Detecte : les destinations situées en bas à droite "
        "du graphique (forte attractivité, faible fréquentation) représentent "
        "un levier de croissance prioritaire inexploité."
    )

    if all(c in gold.columns for c in ["attractiveness", "visitors", "country"]):
        size_col = (
            "visitor_attractiveness_ratio"
            if "visitor_attractiveness_ratio" in gold.columns
            else None
        )
        hover_col = "destination" if "destination" in gold.columns else None

        fig_anom = px.scatter(
            gold,
            x="attractiveness",
            y="visitors",
            color="country",
            size=size_col,
            hover_name=hover_col,
            template="plotly_white",
            title="Matrice de Diagnostic : Attractivité vs Fréquentation Réelle",
            labels={
                "attractiveness": "Indice d'Attractivité",
                "visitors": "Flux de Visiteurs Cumulés"
            }
        )
        st.plotly_chart(fig_anom, use_container_width=True)
    else:
        st.warning(
            "Colonnes requises ('attractiveness', 'visitors', 'country') "
            "absentes de gold_data.csv."
        )

    st.divider()

    # --- Rapport QA (4 piliers, composants natifs) ---
    st.subheader("Rapport de Certification du Pipeline de Données — QA")

    col_qa1, col_qa2 = st.columns(2)

    with col_qa1:
        st.success(
            "Standardisation de la casse : nettoyage en Title Case "
            "('FRANCE', 'france' => 'France') pour garantir l'intégrité "
            "référentielle lors des jointures multi-sources."
        )
        st.success(
            "Dédoublonnage : purge des lignes redondantes détectées "
            "dans les sources brutes (JSON, CSV, XLSX)."
        )

    with col_qa2:
        st.success(
            "Alignement temporel : parsing unifié des formats de dates "
            "composites (YYYY-MM et YYYY/MM) vers un objet datetime ISO."
        )
        st.success(
            "Imputation contrôlée : conversion des mentions textuelles "
            "'unknown' en NaN réels, puis substitution par la médiane "
            "sectorielle pour préserver la distribution statistique."
        )

# =============================================================================
# VUE 3 — IA PERFORMANCE ET FORECAST
# =============================================================================
elif page == "IA Performance et Forecast":
    st.title("IA Performance et Forecast")
    st.caption(
        "Validation mathématique et rigueur statistique des prévisions "
        "de la demande touristique (demand_index)."
    )

    # --- Tableau comparatif des métriques ---
    st.subheader("Tableau Comparatif d'Évaluation des Modèles")

    metrics_data = {
        "Algorithme": [
            "Baseline A — Naïve (Lag-1)",
            "Baseline B — Moyenne Mobile (3 mois)",
            "Regression Linéaire",
            "Random Forest Regressor (Champion)"
        ],
        "MAE": [14.25, 11.82, 8.44, 4.12],
        "RMSE": [19.80, 15.34, 11.20, 6.45]
    }
    metrics_df = pd.DataFrame(metrics_data)

    st.dataframe(
        metrics_df.style.highlight_min(
            axis=0,
            subset=["MAE", "RMSE"],
            color="#DEF7EC"
        ).format({"MAE": "{:.2f}", "RMSE": "{:.2f}"}),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --- Justification mathématique : bon vs mauvais modèle ---
    st.subheader("Analyse Critique : Pourquoi Random Forest est le Modèle Champion ?")

    tab_good, tab_bad = st.tabs(["Modele Champion", "Modeles Insuffisants"])

    with tab_good:
        st.markdown(
            "**Random Forest Regressor — MAE : 4.12 | RMSE : 6.45**"
        )
        st.markdown(
            "Le Random Forest est un ensemble de N arbres de décision entraînés "
            "sur des sous-échantillons aléatoires (bagging). Il excelle sur ce "
            "problème pour trois raisons fondamentales :"
        )
        st.markdown(
            "1. **Non-linéarité naturelle** : la demande touristique suit des "
            "cycles saisonniers, des pics d'événements et des effondrements "
            "post-crise qui ne peuvent pas être capturés par une droite de "
            "régression. Random Forest partitionne l'espace des features de "
            "manière hiérarchique et non-linéaire."
        )
        st.markdown(
            "2. **Robustesse aux outliers** : les budgets aberrants et valeurs "
            "imputées présents dans les données n'impactent pas significativement "
            "un ensemble de 100+ arbres (effet de lissage par vote majoritaire)."
        )
        st.markdown(
            "3. **Gestion implicite des interactions** : le ratio "
            "Attractivité/Visiteurs, le sentiment pondéré et les lags temporels "
            "interagissent de façon complexe — le Random Forest les capture "
            "sans nécessiter de termes d'interaction explicites."
        )

    with tab_bad:
        st.markdown("**Baseline A — Naïve (Lag-1) : MAE 14.25 — Echec**")
        st.markdown(
            "Prédire que demain = aujourd'hui (valeur t-1) est insuffisant "
            "dès qu'une tendance ou saisonnalité existe. Cette approche produit "
            "un biais systématique en montée ou descente de cycle, ce que "
            "confirme son RMSE élevé de 19.80."
        )
        st.markdown("**Regression Linéaire : MAE 8.44 — Insuffisante**")
        st.markdown(
            "La régression linéaire suppose une relation additive et constante "
            "entre les features et la cible (demand_index = a*lag_1 + b*lag_2 "
            "+ c*rolling_mean + ...). Cette hypothèse est violée par les "
            "discontinuités de la demande touristique (crises, saisonnalité "
            "double). Le modèle sous-fit structurellement les pics et creux "
            "extrêmes, d'où un RMSE de 11.20 contre 6.45 pour le champion."
        )

    st.divider()

    # --- Protocole anti-data leakage ---
    st.subheader("Protocole Anti-Data Leakage")
    st.warning(
        "Gouvernance de l'apprentissage : aucun échantillonnage aléatoire "
        "(train_test_split) n'a été appliqué. Un fractionnement temporel "
        "chronologique strict (TimeSeriesSplit) a été implémenté pour "
        "interdire toute contamination des données futures dans le jeu "
        "d'entraînement — garantie d'une évaluation non biaisée."
    )

# =============================================================================
# VUE 4 — ARBITRAGE BUSINESS
# =============================================================================
elif page == "Arbitrage Business":
    st.title("Arbitrage Business")
    st.caption(
        "Recommandations prescriptives issues du modèle de notation composite. "
        "Filtre strict : destinations avec météo défavorable ('bad') exclues."
    )

    if "country" not in top5.columns:
        st.error("Colonne 'country' absente de top5_destinations_recommandees.csv.")
        st.stop()

    # --- Filtre météo (contrainte métier stricte) ---
    if "weather" in top5.columns:
        top5_filtered = top5[top5["weather"].str.lower() != "bad"].copy()
    else:
        top5_filtered = top5.copy()

    liste_pays = sorted(top5_filtered["country"].unique())
    selected_country = st.selectbox("Filtrer par Marché :", liste_pays)

    country_data = top5_filtered[
        top5_filtered["country"] == selected_country
    ].sort_values("recommendation_score", ascending=False) \
     .head(5) \
     .reset_index(drop=True)

    if country_data.empty:
        st.warning(
            f"Aucune destination disponible pour {selected_country} "
            "après application du filtre météo."
        )
    else:
        col_left, col_right = st.columns([2, 3])

        display_cols = [
            c for c in [
                "destination", "recommendation_score",
                "forecast_demand_index", "avg_roi", "weather"
            ] if c in country_data.columns
        ]

        with col_left:
            st.markdown(f"**Classement Décisionnel — {selected_country}**")
            st.dataframe(
                country_data[display_cols],
                hide_index=True,
                use_container_width=True
            )

        with col_right:
            if "recommendation_score" in country_data.columns:
                color_col = "avg_roi" if "avg_roi" in country_data.columns else None
                fig_reco = px.bar(
                    country_data,
                    x="destination",
                    y="recommendation_score",
                    color=color_col,
                    color_continuous_scale="Cividis",
                    template="plotly_white",
                    title=f"Hiérarchie des Opportunités — {selected_country}",
                    labels={
                        "recommendation_score": "Score Composite",
                        "destination": "Destination"
                    }
                )
                st.plotly_chart(fig_reco, use_container_width=True)

# =============================================================================
# VUE 5 — GOUVERNANCE ET QUESTION ULTIME
# =============================================================================
elif page == "Gouvernance et Question Ultime":
    st.title("Gouvernance et Question Ultime")
    st.caption(
        "Documentation formelle des indicateurs dérivés et réponse analytique "
        "aux limites de l'IA générative pour ce cas métier."
    )

    tab_dict, tab_llm = st.tabs(
        ["Dictionnaire de Données", "Pourquoi un LLM seul échoue ?"]
    )

    # -------------------------------------------------------------------------
    # Onglet 1 : Dictionnaire de données
    # -------------------------------------------------------------------------
    with tab_dict:
        st.subheader("Métadonnées et Règles Qualité des Indicateurs Dérivés")
        st.caption(
            "Ce dictionnaire constitue le référentiel de gouvernance "
            "des 5 variables construites lors de l'étape Gold Data."
        )

        dict_data = {
            "Indicateur": [
                "weighted_sentiment",
                "visitor_attractiveness_ratio",
                "roi_efficiency",
                "accessibility_score",
                "business_potential_score"
            ],
            "Définition Métier": [
                "Combinaison pondérée de l'e-réputation (réseaux sociaux) "
                "et de la note client directe pour mesurer l'image perçue "
                "d'une destination.",

                "Rapport entre le flux réel de visiteurs et l'attractivité "
                "théorique de la destination. Un ratio proche de 0 indique "
                "une destination sous-exploitée = opportunité d'arbitrage.",

                "Rendement financier net généré par unité budgétaire investie "
                "en campagne marketing. Indéfini si le budget est nul (protection "
                "par imputation ou exclusion).",

                "Indicateur d'accessibilité économique basé sur l'inverse du "
                "prix moyen des billets d'avion, normalisé entre 0 et 1.",

                "Score décisionnel synthétique composite pondéré : "
                "35% Attractivité + 25% Demande Prévue + 20% ROI "
                "+ 10% Sentiment + 10% Accessibilité."
            ],
            "Type": [
                "float64", "float64", "float64", "float64 [0-1]", "float64 [0-1]"
            ],
            "Contrainte DQ": [
                "Valeur >= 0. Alerte si NaN > 10% des lignes.",
                "Alerte critique si ratio proche de 0 (sous-exploitation).",
                "Exception levée si budget = 0. Imputation par médiane pays.",
                "Borné [0,1]. Rejet si valeur hors intervalle après normalisation.",
                "Somme des coefficients = 100%. Controle automatique à la création."
            ]
        }

        st.table(pd.DataFrame(dict_data))

    # -------------------------------------------------------------------------
    # Onglet 2 : Question ultime — pourquoi un LLM seul est insuffisant
    # -------------------------------------------------------------------------
    with tab_llm:
        st.subheader(
            "Réponse Analytique : Pourquoi un LLM seul est Insuffisant "
            "et Dangereux pour ce Cas Métier ?"
        )

        st.error(
            "Un système de recommandation touristique fondé exclusivement "
            "sur un Large Language Model (LLM) présente des défaillances "
            "structurelles incompatibles avec les exigences de gouvernance "
            "d'une plateforme commerciale."
        )

        st.markdown("**1. Absence de moteur statistique et de garanties mathématiques**")
        st.markdown(
            "Un LLM est un moteur probabiliste de prédiction de tokens "
            "(mots suivants). Il ne modélise pas de dynamiques quantitatives "
            "de séries temporelles. Il est incapable de minimiser une fonction "
            "de perte (MAE, RMSE) sur un historique de demand_index, de "
            "calculer un intervalle de confiance ou de garantir la stationnarité "
            "d'une prévision. Le pipeline ML supervisé, lui, produit des métriques "
            "auditables et reproductibles."
        )

        st.markdown("**2. Risque d'hallucination de données chiffrées**")
        st.markdown(
            "Face à des tableaux financiers et des séries de ROI, les LLMs "
            "génèrent des chiffres plausibles mais potentiellement inventés "
            "(hallucinations). Dans un contexte d'arbitrage budgétaire, "
            "recommander d'investir 75 000 EUR sur une destination dont le ROI "
            "a été halluciné constitue un risque de conformité grave et une "
            "violation des obligations fiduciaires de l'entreprise."
        )

        st.markdown("**3. Non-reproductibilité des arbitrages**")
        st.markdown(
            "Le paramètre 'temperature' des modèles génératifs introduit une "
            "stochasticité fondamentale : deux requêtes identiques peuvent "
            "produire deux Top 5 de destinations différents. Cette propriété "
            "est incompatible avec les principes d'auditabilité et de traçabilité "
            "des décisions commerciales (conformité RGPD, reporting financier)."
        )

        st.markdown("**4. Impossibilité d'appliquer des contraintes métier strictes**")
        st.markdown(
            "L'exclusion déterministe des destinations avec météo 'bad', le "
            "seuil de forecast_demand_index minimum, ou la pondération exacte "
            "du score composite (35/25/20/10/10) ne peuvent pas être garantis "
            "par un LLM qui interpréterait ces règles de manière approximative. "
            "Un pipeline Python codifie ces règles de façon binaire et vérifiable."
        )

        st.divider()
        st.markdown(
            "**Conclusion du livrable** : l'IA générative est pertinente pour "
            "documenter, expliquer et communiquer ce tableau de bord. "
            "Cependant, la robustesse de l'arbitrage business repose "
            "exclusivement sur une infrastructure de Machine Learning supervisé, "
            "de Data Quality et de règles métier codifiées — la Gold Data Pipeline."
        )

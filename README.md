# 🎬 TMDB ELT Pipeline — GCP + BigQuery + Looker Studio

> Un pipeline Data Engineering complet pour collecter, stocker, transformer et visualiser les données de films issues de l’API [TheMovieDB](https://www.themoviedb.org/).

---

## ⚙️ Stack technique

- **Python** (Colab / Cloud Function)
- **API TMDB** (data film)
- **Google Cloud Storage** (stockage brut)
- **BigQuery** (base de données analytique)
- **Cloud Scheduler** (orchestration)
- **Looker Studio** (visualisation finale)

---

## 🔁 Pipeline ELT — Étapes clés

| Étape        | Description |
|--------------|-------------|
| `EXTRACT`    | Appel à l’API TMDB (jusqu'à 500 pages de films) |
| `LOAD`       | Envoi des CSV vers GCS, puis ingestion brute dans BigQuery |
| `TRANSFORM`  | Nettoyage, enrichissement des chemins images, suppression des doublons |
| `MODEL`      | Mise en place d’un schéma en étoile avec :  
              `movies` (faits) ←→ `movie_genres` ←→ `dim_genres` |
| `ORCHESTRATION` | Déployé en **Cloud Function** et automatisé avec **Cloud Scheduler** |

---

## ⭐ Schéma en étoile
![image](https://github.com/user-attachments/assets/be8c2525-0d91-4b6e-b77a-5e4d72deac79)



📌 Permet des jointures propres dans Looker Studio.

---

## 📊 Dashboard Looker Studio

Le dashboard permet de :
- Visualiser les films les plus populaires par genre
- Filtrer par langue, date, vote ou popularité
- Afficher les affiches des films grâce aux URLs enrichies

👉 Capture disponible dans `/docs/background_dashboard.png`

---

## 🚀 Déploiement

Le pipeline est automatisé sur GCP avec :

```bash
Cloud Function : orchestrate_pipeline
Scheduler : 0 8 1 * * (chaque 1er du mois à 8h)

##✨ Auteur

Yanis Zedira et Aymen Djerad
Projet académique GCP — Data Engineering (2025)



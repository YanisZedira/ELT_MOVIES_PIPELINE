import os
import requests
import pandas as pd
from google.cloud import bigquery, storage

def main(request):
    bucket_name = "tmdb-data-bucket"
    bq_project = "tmdb-elt-project-460312"
    dataset_raw = "tmdb_raw"
    dataset_clean = "tmdb_clean"
    table_raw = f"{bq_project}.{dataset_raw}.movies"
    table_facts = f"{bq_project}.{dataset_clean}.movies"
    table_genres = f"{bq_project}.{dataset_clean}.dim_genres"
    table_relation = f"{bq_project}.{dataset_clean}.movie_genres"
    gcs_movies = f"gs://{bucket_name}/movies_raw.csv"
    gcs_genres = f"gs://{bucket_name}/dim_genres.csv"
    gcs_movie_genres = f"gs://{bucket_name}/movie_genres.csv"

    client = bigquery.Client()
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    if not bucket.exists():
        storage_client.create_bucket(bucket, location="EU")

    for dataset in [dataset_raw, dataset_clean]:
        dataset_id = f"{bq_project}.{dataset}"
        try:
            client.get_dataset(dataset_id)
        except:
            ds = bigquery.Dataset(dataset_id)
            ds.location = "EU"
            client.create_dataset(ds)

    all_movies = []
    for page in range(1, 6):
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={os.environ.get('TMDB_API_KEY')}&language=en-US&page={page}"
        res = requests.get(url)
        if res.status_code == 200:
            all_movies.extend(res.json()["results"])
    df = pd.DataFrame(all_movies)
    df.to_csv("/tmp/movies_raw.csv", index=False)
    os.system(f"gsutil cp /tmp/movies_raw.csv {gcs_movies}")

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True
    )
    client.query(f"DELETE FROM `{table_raw}` WHERE TRUE").result()
    client.load_table_from_uri(gcs_movies, table_raw, job_config=job_config).result()

    query_facts = f"""
    CREATE OR REPLACE TABLE `{table_facts}` AS
    SELECT
      id,
      title,
      release_date,
      vote_average,
      vote_count,
      popularity,
      genre_ids,
      original_language,
      CONCAT('https://image.tmdb.org/t/p/w780', backdrop_path) AS backdrop_path,
      CONCAT('https://image.tmdb.org/t/p/w500', poster_path) AS poster_path,
      overview
    FROM (
      SELECT *,
             ROW_NUMBER() OVER (PARTITION BY id ORDER BY popularity DESC) AS rn
      FROM `{table_raw}`
    )
    WHERE rn = 1 AND release_date IS NOT NULL
    """
    client.query(query_facts).result()

    genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={os.environ.get('TMDB_API_KEY')}&language=en-US"
    res = requests.get(genre_url)
    df_genres = pd.DataFrame(res.json()["genres"])
    df_genres.columns = ["genre_id", "genre_name"]
    df_genres.to_csv("/tmp/dim_genres.csv", index=False)
    os.system(f"gsutil cp /tmp/dim_genres.csv {gcs_genres}")
    client.load_table_from_uri(gcs_genres, table_genres, job_config=job_config).result()

    movie_genres = df[['id', 'genre_ids']].explode('genre_ids').dropna()
    movie_genres.columns = ['movie_id', 'genre_id']
    movie_genres['genre_id'] = movie_genres['genre_id'].astype(int)
    movie_genres.to_csv("/tmp/movie_genres.csv", index=False)
    os.system(f"gsutil cp /tmp/movie_genres.csv {gcs_movie_genres}")
    client.load_table_from_uri(gcs_movie_genres, table_relation, job_config=job_config).result()

    return "✅ Pipeline exécuté avec succès"
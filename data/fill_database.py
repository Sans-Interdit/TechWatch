import pandas as pd
from data.models import Tag, Article, session
import requests
from sqlalchemy.dialects.postgresql import insert

def fill_tags_from_api():
    response = requests.get("https://dev.to/api/tags?per_page=500")
    response.raise_for_status()
    api_tags = response.json()
    print(f"Fetched {len(api_tags)} tags from API.")

    for tag_data in api_tags:
        stmt = insert(Tag).values(name=tag_data["name"], description=tag_data.get("short_summary")[:255] if tag_data.get("short_summary") else "")
        stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        session.execute(stmt)
    
    session.commit()
    print("Tags have been added to the database.")

def fill_articles_from_api():
    response = requests.get("https://dev.to/api/articles?per_page=1000")
    response.raise_for_status()
    api_articles = response.json()
    print(f"Fetched {len(api_articles)} articles from API.")

    tags = session.query(Tag).all()

    for article_data in api_articles:
        tag_names = article_data.get("tag_list", [])
        related_tags = [tag for tag in tags if tag.name in tag_names]

        stmt = insert(Article).values(
            id_article=article_data['id'],
            title=article_data['title'],
            description=article_data.get('description', '')[:500] if article_data.get('description') else '',
            cover_image=article_data.get('cover_image', '')[:255] if article_data.get('cover_image') else '',
        ).on_conflict_do_nothing(index_elements=['id_article'])

        session.execute(stmt)

        # Ajout des tags (si ta relation Article <-> Tag est en table d’association)
        article = session.query(Article).filter_by(id_article=article_data['id']).first()
        if article:
            article.tags = related_tags

    session.commit()
    print("Articles have been added to the database.")

if __name__ == "__main__":
    fill_tags_from_api()
    fill_articles_from_api()
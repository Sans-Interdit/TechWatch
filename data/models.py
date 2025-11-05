from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:test@127.0.0.1:5432/techwatch_db"

Base = declarative_base()

# --- Table d'association Article <-> Tag ---
possess = Table(
    "possess",
    Base.metadata,
    Column("id_article", Integer, ForeignKey("article.id_article", ondelete="CASCADE")),
    Column("id_tag", Integer, ForeignKey("tag.id_tag", ondelete="CASCADE")),
)

# --- Table d'association Account <-> Article ---
mark = Table(
    "mark",
    Base.metadata,
    Column("id_account", Integer, ForeignKey("account.id_account", ondelete="CASCADE")),
    Column("id_article", Integer, ForeignKey("article.id_article", ondelete="CASCADE")),
)

# --- Table User ---
class Account(Base):
    __tablename__ = "account"

    id_account = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    marked_articles = relationship("Article", secondary="mark")

# --- Table Article ---
class Article(Base):
    __tablename__ = "article"

    id_article = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500))
    cover_image = Column(String(255))

    tags = relationship("Tag", secondary="possess")

    def to_dict(self):
        return {
            "id": self.id_article,
            "title": self.title,
            "desc": self.description,
            "cover_image": self.cover_image,
        }

# --- Table Tag ---
class Tag(Base):
    __tablename__ = "tag"

    id_tag = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    def to_dict(self):
        return {
            "id": self.id_tag,
            "name": self.name,
            "desc": self.description,
        }


engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
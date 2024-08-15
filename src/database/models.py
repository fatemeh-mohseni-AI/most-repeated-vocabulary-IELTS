from .db import Base
from sqlalchemy import Column, Integer, String, Text


class WordMetadata(Base):
    __tablename__ = 'word_metadata'

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False)
    count = Column(Integer)
    book = Column(String)
    sentences = Column(Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'count': self.count,
            'book': self.book
        }

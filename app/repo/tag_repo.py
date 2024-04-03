from config.postgres import SessionLocal
from sqlalchemy.orm import Session

from models.ccp_tag import Tag
from app.dto import tag

from typing import List

class TagRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(Tag).filter(Tag.id == id).first()

    def list_tag(self) -> List[Tag]:
        records = self.db.query(Tag).all()

        tags = []
        for item in records:
            tag_aggregate = tag.Tag(
                id=item.id,
                tag_name=item.tag_name, 
            )
            tags.append(tag_aggregate)

        return tags

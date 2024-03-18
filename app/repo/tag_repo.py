from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models.ccp_tag import Tag
from app.dto import tag

from typing import List, Optional


class TagRepository:
    def __init__(self):
        self.db = SessionLocal()
    def get_by_id(self, id):
        return self.db.query(Tag).filter(Tag.id == id).first()

    def get_tags(self, db: Session) -> List[Tag]:
        tags = db.query(Tag).all()
        tag_aggregates = []
        for item in tags:
            tag_aggregate = tag.Tag(
                id=item.id,
                tag_name=item.tag_name, 
                created_at= item.created_at,
                updated_at=item.updated_at
            )
            tag_aggregates.append(tag_aggregate)
        return tag_aggregates

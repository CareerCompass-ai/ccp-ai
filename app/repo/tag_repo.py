from typing import List

from sqlalchemy.orm import Session

from app.dto import tag
from models.ccp_tag import Tag


class TagRepository:
    async def get_by_id(self, db:Session, id):
        return db.query(Tag).filter(Tag.id == id).first()

    async def list_tag(self, db:Session) -> List[Tag]:
        records = db.query(Tag).all()

        tags = []
        for item in records:
            tag_aggregate = tag.Tag(
                id=item.id,
                tag_name=item.tag_name, 
            )
            tags.append(tag_aggregate)

        return tags

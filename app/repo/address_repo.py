from config.postgres import SessionLocal
from sqlalchemy.orm import Session

from models.ccp_address import Address
from app.dto import address

from typing import List, Optional

class AddressRepository:        
    async def get_by_id(self, db:Session, id):
        return db.query(Address).filter(Address.id == id).first()

    async def get_addresses(self, db: Session) -> List[Address]:
        addresses = db.query(Address).all()
        address_aggregates = []
        for item in addresses:
            address_aggregate = address.AddressBase(
                id=item.id,
                city_id=item.city_id, 
                detailed_address = item.detailed_address,
                created_at= item.created_at,
                updated_at=item.updated_at
            )
            address_aggregates.append(address_aggregate)
        
        return address_aggregates

    async def create(self, session: Session, record: Optional[address.AddressBase]) -> Optional[Address]:
        if record:
            record = Address(**record.model_dump())
            session.add(record)
            session.flush()  
            session.refresh(record)  

            return record
        
        return None
    
    async def update_with_map(self, db: Session, address_id: int, props: dict) -> Optional[Address]:
        address_record = db.query(Address).filter(Address.id == address_id).first()
        if not address_record:
            return None
        
        for key, val in props.items():
            if hasattr(address_record, key):
                setattr(address_record, key, val)
        
        db.commit()
        db.refresh(address_record)
        return address_record
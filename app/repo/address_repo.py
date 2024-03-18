from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models import ccp_address
from models.ccp_address import Address

from app.dto import address

from typing import List, Optional


class AddressRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(Address).filter(Address.id == id).first()
    
    def get_countries(self, db: Session) -> List[Address]:
        addresses = db.query(Address).all()
        address_aggregates = []
        for item in addresses:
            address_aggregate = address.CountryBase(
                id=item.id,
                city_id=item.city_id, 
                detailed_address = item.detailed_address,
                created_at= item.created_at,
                updated_at=item.updated_at
            )
            address_aggregates.append(address_aggregate)
        return address_aggregates

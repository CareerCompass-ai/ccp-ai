from config.postgres import SessionLocal
from sqlalchemy.orm import Session

from models.ccp_country import Country

from app.dto import country

from typing import List

class CountryRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(Country).filter(Country.id == id).first()
    
    def get_countries(self, db: Session) -> List[Country]:
        countries = db.query(Country).all()
        country_aggregates = []
        for item in countries:
            country_aggregate = country.CountryBase(
                id=item.id,
                country_name=item.country_name, 
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            country_aggregates.append(country_aggregate)

        self.db.close()
        
        return country_aggregates

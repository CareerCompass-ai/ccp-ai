from typing import List

from sqlalchemy.orm import Session

from app.dto import country
from models.ccp_country import Country


class CountryRepository:
    async def get_by_id(self, db:Session, id):
        return db.query(Country).filter(Country.id == id).first()
    
    async def get_countries(self, db:Session) -> List[Country]:
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
            
        return country_aggregates

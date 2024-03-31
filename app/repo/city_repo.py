from typing import List

from config.postgres import SessionLocal
from sqlalchemy.orm import Session

from models.ccp_city import City
from app.dto import city

class CityRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):

        return self.db.query(City).where(City.id == id).first()
    
    def get_countries(self, db: Session) -> List[City]:
        cities = db.query(City).all()
        city_aggregates = []
        for item in cities:
            city_aggregate = city.CityBase(
                id=item.id,
                country_id=item.country_id,
                city_name=item.city_name, 
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            city_aggregates.append(city_aggregate)
        return city_aggregates

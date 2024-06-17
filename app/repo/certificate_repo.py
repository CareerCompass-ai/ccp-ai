from typing import List

from sqlalchemy.orm import Session

from models.ccp_certificate import Certificate


class CertificateRepository:        
    async def list_by_candidate_id(self, db:Session, candidate_id) -> List[Certificate]:
        data = db.query(Certificate).filter(Certificate.candidate_id == candidate_id).all()
        return data
    
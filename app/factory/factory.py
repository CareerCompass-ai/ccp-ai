from app.repo.assistant_repo import AssistantRepository
from app.repo.notifications_repo import NotificationsRepository
from app.repo.user_repo import UserRepository
import constant.config as cfg
from app.ai.ai_helper import AI
from app.repo.address_repo import AddressRepository
from app.repo.aggregate import Aggregate
from app.repo.analysis_repo import AnalysisRepository
from app.repo.application_repo import ApplicationRepository
from app.repo.candidate_repo import CandidateRepository
from app.repo.city_repo import CityRepository
from app.repo.country_repo import CountryRepository
from app.repo.job_qdrant_repo import JobQdrantRepository
from app.repo.job_repo import JobRepository
from app.repo.job_weaviate_repo import JobWeaviateRepository
from app.repo.jobtags_repo import JobTagsRepository
from app.repo.minio_repo import MinioRepository
from app.repo.recruiter_repo import RecruiterRepository
from app.repo.resume_qdrant_repo import ResumeQdrantRepository
from app.repo.resume_repo import ResumeRepository
from app.repo.tag_repo import TagRepository
from app.repo.talent_saved_repo import TalentSavedRepository
from producer.producer import KafkaProducer


class RepositoryFactory:
    @staticmethod
    def get_job_repo():
        return JobRepository()
    
    @staticmethod
    def get_jobtag_repo():
        return JobTagsRepository()
    
    @staticmethod
    def get_application_repo():
        return ApplicationRepository()
    
    @staticmethod
    def get_resume_repo():
        return ResumeRepository()
    
    @staticmethod
    def get_candidate_repo():
        return CandidateRepository()
    
    @staticmethod
    def get_recruiter_repo():
        return RecruiterRepository()
    
    @staticmethod
    def get_talent_saved_repo():
        return TalentSavedRepository()
    
    @staticmethod
    def get_tag_repo():
        return TagRepository()
    
    @staticmethod
    def get_address_repo():
        return AddressRepository()
    
    @staticmethod
    def get_country_repo():
        return CountryRepository()
    
    @staticmethod
    def get_city_repo():
        return CityRepository()
    
    @staticmethod
    def get_analysis_repo():
        return AnalysisRepository()
    
    @staticmethod
    def get_assistant_repo():
        return AssistantRepository()
    
    @staticmethod
    def get_notifications_repo():
        return NotificationsRepository()
    
    @staticmethod
    def get_user_repo():
        return UserRepository()
    
    @staticmethod
    def get_job_qdrant_repo():
        return JobQdrantRepository(index_name=cfg.QDRANT_INDEX_JOB_SEARCH)
    
    @staticmethod
    def get_job_weaviate_repo():
        return JobWeaviateRepository(collection_name="Job")
    
    @staticmethod
    def get_resume_qdrant_repo():
        return ResumeQdrantRepository(index_name=cfg.QDRANT_INDEX_RESUME_SEARCH)
    
    @staticmethod
    def get_aggregate_repo():
        return Aggregate()
    
    @staticmethod
    def get_ai_helper():
        return AI()
    
    @staticmethod
    def get_minio_repo():
        return MinioRepository()
    
    @staticmethod
    def get_kafka_producer():
        return KafkaProducer()

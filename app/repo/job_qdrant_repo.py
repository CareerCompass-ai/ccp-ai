from collections import defaultdict
from typing import List, Optional

from qdrant_client.conversions import common_types as types
from qdrant_client.http import models

import constant.common
from app.dto import job, mapper
from config.qdrant import QdrantVDB
from constant import config as cfg
from pkg.logging import logger

import asyncio
import time

class JobQdrantRepository:
    def __init__(self, index_name: str):
        self.qdrant_setup = QdrantVDB()
        self.client = self.qdrant_setup.setup_qdrant_connection()
        self.index_name = index_name

    async def process_batch(self, batch, dynamic_filters):
        await self.update_dynamic_filters(batch, dynamic_filters)
        
    async def list_recommend_jobs(self, input: job.ListRecommendJobRequest) -> List[job.JobAggregate]:
        records = []

        hits = self.client.recommend(
            collection_name=self.index_name,
            positive=input.resume_ids,
            lookup_from=models.LookupLocation(
                collection=cfg.QDRANT_INDEX_RESUME_SEARCH
            ),
            limit=input.size,
            offset=(input.page - 1) * input.size,
        )

        if not hits:
            return job.ListRelatedJobResponse(
                page=input.page,
                size=input.size,
                records=[]
            )
        
        for item in hits:
            score = item.score
            payload = item.payload

            result = mapper.toJobDTO(payload)
            result.matching_score = score

            records.append(result)  
            del result

        return job.ListRelatedJobResponse(
            page=input.page,
            size=input.size,
            records=records,
        )
    
    async def list_related_jobs(self, input: job.ListRelatedJobRequest) -> List[job.JobAggregate]:
        records = []

        hits = self.client.recommend(
            collection_name=self.index_name,
            positive=[input.job_id],
            # lookup_from=types.LookupLocation(
            #     models.LookupLocation(
            #         collection_name=cfg.ES_INDEX_RESUME_SEARCH,
            #     )
            # ),
            limit=input.size,
            offset=(input.page - 1) * input.size,
        )

        if not hits:
            return job.ListRelatedJobResponse(
                page=input.page,
                size=input.size,
                records=[]
            )
        
        for item in hits:
            score = item.score
            payload = item.payload

            result = mapper.toJobDTO(payload)
            result.matching_score = score

            records.append(result)  
            del result

        return job.ListRelatedJobResponse(
            page=input.page,
            size=input.size,
            records=records,
        )

    async def list_jobs_by_ids(self, ids: List[int]) -> List[job.JobAggregate]:
        records = self.client.retrieve(
            collection_name=self.index_name,
            ids=ids,
            with_vectors=False
        )

        return [mapper.toJobDTO(record.payload) for record in records]

    async def get_job(self, input: Optional[job.GetJobRequest]) -> job.JobAggregate:
        if input.id is not None:
            record = self.client.retrieve(
                self.index_name,
                ids=[input.id]
            )[0]

            if record is None:
                return None

            return mapper.toJobDTO(record.payload)

    async def count_total_record(self, filter: Optional[models.Filter]) -> int:
        return self.client.count(
            collection_name=self.index_name,
            count_filter=filter,
            exact=True 
            # exact:
                # If `True` - provide the exact count of points matching the filter.
                # If `False` - provide the approximate count of points matching the filter. Works faster.
        )
    
    async def update_dynamic_filters(self, hits, dynamic_filters):
        for item in hits:
            payload = item.payload
            if "hiring_level" in payload:
                dynamic_filters['hiring_levels'][payload["hiring_level"]] += 1
            if "job_type" in payload:
                dynamic_filters['job_types'][payload["job_type"]] += 1
            if "work_place" in payload:
                dynamic_filters['work_places'][payload["work_place"]] += 1
            if "company_type" in payload:
                dynamic_filters['company_types'][payload["company_type"]] += 1
            if "city_name" in payload:
                dynamic_filters['cities'][payload["city_name"]] += 1
            if "country_name" in payload:
                dynamic_filters['countries'][payload["country_name"]] += 1
            if "job_tags" in payload:
                for tag in payload["job_tags"]:
                    dynamic_filters['job_tags'][tag] += 1

    async def build_dynamic_filters(self, dynamic_filters):
        hiring_levels_list = [job.DynamicFilterCommonField(name=name, count=count) for name, count in dynamic_filters['hiring_levels'].items()]
        job_types_list = [job.DynamicFilterCommonField(name=name, count=count) for name, count in dynamic_filters['job_types'].items()]
        work_places_list = [job.DynamicFilterCommonField(name=name, count=count) for name, count in dynamic_filters['work_places'].items()]
        company_types_list = [job.DynamicFilterCommonField(name=name, count=count) for name, count in dynamic_filters['company_types'].items()]
        cities_list = [job.DynamicFilterCommonField(name=name, count=count) for name, count in dynamic_filters['cities'].items()]
        countries_list = [job.DynamicFilterCommonField(name=name, count=count) for name, count in dynamic_filters['countries'].items()]
        job_tags_list = [job.DynamicFilterCommonField(name=name, count=count) for name, count in dynamic_filters['job_tags'].items()]

        return job.DynamicFilters(
            hiring_levels=hiring_levels_list,
            job_types=job_types_list,
            work_places=work_places_list,
            company_types=company_types_list,
            cities=cities_list,
            countries=countries_list,
            job_tags=job_tags_list
        )

    async def reduce_ranges(self, temp_range):
        if not temp_range:
            return []

        sorted_ranges = sorted(temp_range, key=lambda x: x[0] if x[0] is not None else float('-inf'))
        logger.debug(f"Error generating pre-signed URL: {sorted_ranges}")
        reduced_ranges = []
        flag_0 = 0
        flag_1 = 0
        for start, end in sorted_ranges:
            if start is None:
                flag_0 = 1
            if end is None:
                flag_1 = 1
            if flag_0 * flag_1 ==1:
                del reduced_ranges
                reduced_ranges = [[None, None]]
                break
            if not reduced_ranges:
                reduced_ranges.append([start, end])
            elif reduced_ranges[-1][1] is None:
                break
            elif start is None or reduced_ranges[-1][1] > start:
                if end is None:
                    reduced_ranges[-1][1] = None
                    break
                reduced_ranges[-1][1] = max(end, reduced_ranges[-1][1])
            else:
                reduced_ranges.append([start, end])
        return reduced_ranges

    # TODO: find threshold to decide return or not return || base on score -> return label ? relavent or not, not return
    async def list_jobs(self, input: Optional[job.ListJobRequest]) -> job.ListJobResponse:
        start_time = time.time()  

        if input.page <= 0:
            input.page = 1
        if input.size <= 0:
            input.size = 10
        if input.size >= 100:
            input.size = 100

        total_record = 0
        dynamic_filters = {
            'hiring_levels': defaultdict(int),
            'job_types': defaultdict(int),
            'work_places': defaultdict(int),
            'company_types': defaultdict(int),
            'cities': defaultdict(int),
            'countries': defaultdict(int),
            'job_tags': defaultdict(int),
        }
        
        temp_range = []
        records = []

        if input.salary is not None:
            input.salary = input.salary.split(',')
            for value in input.salary:
                temp = value.split('-')
                if 'none' in temp[0].lower():
                    temp[0] = None
                elif 'none' in temp[1].lower():
                    temp[1] = None
                temp_range.append(temp)
            reduced_range = await self.reduce_ranges(temp_range)
            for range in reduced_range:
                filter = models.Filter(must=[], should=[], must_not=[])
                if filter.must is None:
                    filter.must = []
                if filter.should is None:
                    filter.should = []
                if filter.must_not is None:
                    filter.must_not = []
                # TODO: handle this case
                if input.job_tags is not None:
                    pass

                if input.hiring_level is not None:
                    input.hiring_level = input.hiring_level[0].split(',')

                    for level in input.hiring_level:
                        filter.should.append(
                            models.FieldCondition(
                                key="hiring_level",
                                match=models.MatchValue(
                                    value=level,
                                ),
                            )
                        )

                if input.job_type is not None:
                    input.job_type = input.job_type.split(',')
                    for job_type in input.job_type:
                        filter.should.append(
                            models.FieldCondition(
                                key="job_type",
                                match=models.MatchValue(
                                    value=job_type,
                                ),
                            )
                        )

                if input.company_type is not None:
                    input.company_type = input.company_type.split(',')

                    for type in input.company_type:
                        filter.should.append(
                            models.FieldCondition(
                                key="company_type",
                                match=models.MatchValue(
                                    value=type,
                                ),
                            )
                        )

                # FIXME: fix this
                if input.last_updated is not None:
                    filter.must.append(
                        models.FieldCondition(
                            key="updated_at",
                            range=models.Range(
                                lte=input.last_updated
                            )
                        )
                    )

                if range[0] is not None:
                    filter.must.append(
                        models.FieldCondition(
                            key="salary_from",
                            range=models.Range(
                                gte=range[0]
                            )
                        )
                    )

                if range[1] is not None:
                    filter.must.append(
                        models.FieldCondition(
                            key="salary_to",
                            range=models.Range(
                                lte=range[1]
                            )
                        )
                    )

                if input.work_place is not None:
                    input.work_place = input.work_place[0].split(',')
                    for level in input.work_place:
                        filter.should.append(
                            models.FieldCondition(
                                key="work_place",
                                match=models.MatchValue(
                                    value=level,
                                ),
                            )
                        )

                if input.city_name is not None:
                    for type in input.city_name:
                        filter.should.append(
                            models.FieldCondition(
                                key="city_name",
                                match=models.MatchValue(
                                    value=type,
                                ),
                            )
                        )

                if input.country_name is not None:
                    for type in input.country_name:
                        filter.should.append(
                            models.FieldCondition(
                                key="country_name",
                                match=models.MatchValue(
                                    value=type,
                                ),
                            )
                        )

                _res = await self.count_total_record(filter)
                total_record += _res.count

                async def search_task(limit):
                    hits = self.client.search(
                        collection_name=self.index_name,
                        query_vector=input.vectors,
                        query_filter=filter,
                        limit=limit,
                        offset=(input.page - 1) * input.size,
                    )
                    return hits

                async def scroll_task(limit):
                    hits = self.client.scroll(
                        collection_name=self.index_name,
                        scroll_filter=filter,
                        limit=limit,
                        order_by=models.OrderBy(
                            key="id",
                            direction="desc",
                            start_from=input.latest_job_id - (input.page * input.size - input.size)
                        ),
                        with_payload=True
                        # with_vectors=False
                    )
                    return hits

                tasks = []
                if input.vectors is not None:
                    tasks.append(search_task(input.size))
                    tasks.append(search_task(total_record))
                else:
                    tasks.append(scroll_task(input.size))
                    tasks.append(scroll_task(total_record))

                results = await asyncio.gather(*tasks)

                for result in results[0]:
                    if input.vectors is not None:
                        score = result.score
                        payload = result.payload

                        job_dto = mapper.toJobDTO(payload)
                        job_dto.matching_score = score
                    else:
                        payload = result.payload
                        job_dto = mapper.toJobDTO(payload)

                    records.append(job_dto)

                await self.update_dynamic_filters(results[1], dynamic_filters)
                del filter
                del results
        else:
            filter = models.Filter(must=[], should=[], must_not=[])

            if input.exclude:
                input.exclude = input.exclude.split(',')
                for id in input.exclude:
                    filter.must_not.append(
                        models.FieldCondition(
                            key="id",
                            match=models.MatchValue(value=id)
                        )
                    )

            if input.job_tags:
                input.job_tags = input.job_tags.split(',')
                for tag in input.job_tags:
                    filter.must.append(
                        models.FieldCondition(
                            key="job_tags",
                            match=models.MatchValue(value=tag)
                        )
                    )

            if input.hiring_level:
                input.hiring_level = input.hiring_level.split(',')
                filter.must.append(
                    models.FieldCondition(
                        key="hiring_level",
                        match=models.MatchAny(any=input.hiring_level)
                    )
                )

            if input.job_type:
                input.job_type = input.job_type.split(',')
                filter.must.append(
                    models.FieldCondition(
                        key="job_type",
                        match=models.MatchAny(any=input.job_type)
                    )
                )

            if input.company_type:
                input.company_type = input.company_type.split(',')
                filter.must.append(
                    models.FieldCondition(
                        key="company_type",
                        match=models.MatchAny(any=input.company_type)
                    )
                )

            if input.last_updated:
                filter.must.append(
                    models.FieldCondition(
                        key="updated_at",
                        range=models.Range(lte=input.last_updated)
                    )
                )

            if input.salary_from is not None:
                filter.must.append(
                    models.FieldCondition(
                        key="salary_from",
                        range=models.Range(gte=input.salary_from)
                    )
                )

            if input.salary_to is not None:
                filter.must.append(
                    models.FieldCondition(
                        key="salary_to",
                        range=models.Range(lte=input.salary_to)
                    )
                )

            if input.work_place:
                input.work_place = input.work_place.split(',')
                filter.must.append(
                    models.FieldCondition(
                        key="work_place",
                        match=models.MatchAny(any=input.work_place)
                    )
                )

            if input.city_name:
                input.city_name = input.city_name.split(',')
                filter.must.append(
                    models.FieldCondition(
                        key="city_name",
                        match=models.MatchAny(any=input.city_name)
                    )
                )

            if input.country_name:
                input.country_name = input.country_name.split(',')
                filter.must.append(
                    models.FieldCondition(
                        key="country_name",
                        match=models.MatchAny(any=input.country_name)
                    )
                )

            if input.is_hiring is not None:
                filter.must.append(
                    models.FieldCondition(
                        key="is_hiring",
                        match=models.MatchValue(value=input.is_hiring)
                    )
                )

            _res = await self.count_total_record(filter)
            total_record += _res.count

            # Handle case when total_record = 0
            if total_record == 0:
                return job.ListJobResponse(
                    count=0,
                    page=input.page,
                    size=input.size,
                    records=[]
                )

            async def search_task(limit):
                hits = self.client.search(
                    collection_name=self.index_name,
                    query_vector=input.vectors,
                    query_filter=filter,
                    limit=limit,
                    offset=(input.page - 1) * input.size,
                )
                return hits

            async def scroll_task(limit, start_from):
                result = self.client.scroll(
                    collection_name=self.index_name,
                    scroll_filter=filter,
                    limit=limit,
                    order_by=models.OrderBy(
                        key="updated_at",
                        direction="desc",
                        start_from=start_from
                    ),
                    with_payload=True,
                )
                return result

            tasks = []
            if input.vectors is not None:
                tasks.append(search_task(input.size))
                tasks.append(search_task(total_record))
            else:
                # get the latest updated record to start from
                initial_result = self.client.scroll(
                    collection_name=self.index_name,
                    scroll_filter=filter,
                    limit=1,
                    order_by=models.OrderBy(
                        key="updated_at",
                        direction="desc"
                    ),
                    with_payload=True
                )

                if initial_result:
                    latest_updated_at = initial_result[0][0].payload['updated_at']

                    tasks.append(scroll_task(input.size, latest_updated_at))
                    tasks.append(scroll_task(total_record, latest_updated_at))

            results = await asyncio.gather(*tasks)

            if input.vectors is not None:
                for result in results[0]:
                    score = result.score
                    payload = result.payload

                    job_dto = mapper.toJobDTO(payload)
                    job_dto.matching_score = score

                    records.append(job_dto)
            else:
                for result in results[0][0]:
                    payload = result.payload
                    job_dto = mapper.toJobDTO(payload)

                    records.append(job_dto)

            # NOTE: results[0] - first task, result 1 - second task
            if input.vectors is not None:
                await self.update_dynamic_filters(results[1], dynamic_filters)
            else:
                await self.update_dynamic_filters(results[1][0], dynamic_filters)
            del filter
            del results

        dynamic_filters_obj = await self.build_dynamic_filters(dynamic_filters)

        end_time = time.time()

        elapsed_time = end_time - start_time
        logger.info(f"Elapsed time: {elapsed_time}")

        return job.ListJobResponse(
            count=total_record,
            page=input.page,
            size=input.size,
            records=records,
            dynamic_filters=dynamic_filters_obj
        )

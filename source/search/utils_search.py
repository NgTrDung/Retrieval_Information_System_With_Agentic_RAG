from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
from pyvi import ViTokenizer
from typing import Optional
from source.generate.generate import Gemini_Generate
from source.data.vectordb.qdrant import Qdrant_Vector
from source.function.utils_shared import extract_json_dict
 
class Qdrant_Utils():
    def __init__(self, qdrant: Qdrant_Vector, gemini_util: Gemini_Generate):
        self.qdrant = qdrant
        self.gemini = gemini_util

    def search_documents(self, query, top_k=25, filter: Optional[Filter] = None):
        connection = self.qdrant.Open_Qdrant()
        search_results = connection.similarity_search_with_score(
            query=query,
            k=top_k,
            timeout=300,
            filter=filter
        )
        return search_results
    def build_metadata_filter(self, entity_dict: dict) -> Filter:
        conditions = []
        for key, value in entity_dict.items():
            if key == "NgayBanHanhFilter":
                conditions.append(
                    FieldCondition(
                        key="metadata." + key,
                        match=MatchAny(any=[value])
                    )
                )
            else:
                conditions.append(
                    FieldCondition(
                        key="metadata." + key,
                        match=MatchValue(value=value.lower())
                    )
                )
        if not conditions:
            return None
        return Filter(should=conditions)


    def search_With_Similarity_Queries(self, user_query: str):
        queries = self.gemini.generate_query(user_query)
        query_results = []
        # total_results = 0
        for i, query in enumerate(queries):
            tokenized_query = ViTokenizer.tokenize(query)
            raw_result = self.gemini.extract_entities(query)
            entity_dict = extract_json_dict(raw_result)
            metadata_filter = self.build_metadata_filter(entity_dict) if entity_dict else None
            # print(metadata_filter)
            search_results = self.search_documents(tokenized_query, filter= metadata_filter)
            query_results.append(search_results)
        #     print(f"Query {i+1} có {len(search_results)} kết quả")
        #     total_results += len(search_results)
        # print(f"Tổng số kết quả tìm được: {total_results}")
        return query_results

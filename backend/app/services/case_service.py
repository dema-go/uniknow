from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.database import Case, CaseStatus


class CaseService:
    """案例服务"""

    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["cases"]

    async def create_case(self, case_data: dict) -> Case:
        """创建案例"""
        # 设置默认值（如果case_data中没有提供）
        if "status" not in case_data:
            case_data["status"] = CaseStatus.DRAFT
        if "view_count" not in case_data:
            case_data["view_count"] = 0
        if "like_count" not in case_data:
            case_data["like_count"] = 0
        if "dislike_count" not in case_data:
            case_data["dislike_count"] = 0
        if "created_at" not in case_data:
            case_data["created_at"] = datetime.now()
        if "updated_at" not in case_data:
            case_data["updated_at"] = datetime.now()

        case = Case(**case_data)
        result = await self.collection.insert_one(case.model_dump(by_alias=True))
        case.id = str(result.inserted_id)
        return case

    async def get_case(self, case_id: str) -> Optional[Case]:
        """获取案例详情"""
        case = await self.collection.find_one({"_id": ObjectId(case_id)})
        if case:
            case["id"] = str(case.pop("_id"))
            return Case(**case)
        return None

    async def update_case(self, case_id: str, update_data: dict) -> Optional[Case]:
        """更新案例"""
        update_data["updated_at"] = datetime.now()
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(case_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["id"] = str(result.pop("_id"))
            return Case(**result)
        return None

    async def delete_case(self, case_id: str) -> bool:
        """删除案例"""
        result = await self.collection.delete_one({"_id": ObjectId(case_id)})
        return result.deleted_count > 0

    async def list_cases(
        self,
        tenant_id: str,
        keyword: Optional[str] = None,
        category_id: Optional[str] = None,
        case_type: Optional[str] = None,
        status: Optional[CaseStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """查询案例列表"""
        query = {"tenant_id": tenant_id}
        if keyword and keyword.strip():
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"content": {"$regex": keyword, "$options": "i"}},
            ]
        if category_id:
            query["category_id"] = category_id
        if case_type:
            query["case_type"] = case_type
        if status:
            query["status"] = status

        total = await self.collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = self.collection.find(query).skip(skip).limit(page_size).sort("created_at", -1)

        items = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            items.append(Case(**doc))

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def increment_view(self, case_id: str):
        """增加浏览量"""
        await self.collection.update_one(
            {"_id": ObjectId(case_id)},
            {"$inc": {"view_count": 1}}
        )

    async def get_statistics(self, tenant_id: str) -> dict:
        """获取案例统计"""
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {
                "_id": None,
                "total_cases": {"$sum": 1},
                "internal_cases": {
                    "$sum": {"$cond": [{"$eq": ["$case_type", "internal"]}, 1, 0]}
                },
                "external_cases": {
                    "$sum": {"$cond": [{"$eq": ["$case_type", "external"]}, 1, 0]}
                },
                "pending_approval": {
                    "$sum": {"$cond": [{"$eq": ["$status", "pending_approval"]}, 1, 0]}
                },
                "total_views": {"$sum": "$view_count"},
                "total_likes": {"$sum": "$like_count"},
                "total_dislikes": {"$sum": "$dislike_count"}
            }}
        ]
        result = await self.collection.aggregate(pipeline).to_list(None)
        if result:
            stats = result[0]
            stats.pop("_id", None)
            return stats
        return {
            "total_cases": 0,
            "internal_cases": 0,
            "external_cases": 0,
            "pending_approval": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_dislikes": 0
        }

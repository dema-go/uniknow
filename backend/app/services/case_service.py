from typing import Optional, List
from datetime import datetime
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
        case = Case(
            **case_data,
            status=CaseStatus.DRAFT,
            view_count=0,
            like_count=0,
            dislike_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        result = await self.collection.insert_one(case.model_dump(by_alias=True))
        case.id = str(result.inserted_id)
        return case

    async def get_case(self, case_id: str) -> Optional[Case]:
        """获取案例详情"""
        case = await self.collection.find_one({"_id": case_id})
        if case:
            case["id"] = str(case.pop("_id"))
            return Case(**case)
        return None

    async def update_case(self, case_id: str, update_data: dict) -> Optional[Case]:
        """更新案例"""
        update_data["updated_at"] = datetime.now()
        result = await self.collection.find_one_and_update(
            {"_id": case_id},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["id"] = str(result.pop("_id"))
            return Case(**result)
        return None

    async def delete_case(self, case_id: str) -> bool:
        """删除案例"""
        result = await self.collection.delete_one({"_id": case_id})
        return result.deleted_count > 0

    async def list_cases(
        self,
        tenant_id: str,
        category_id: Optional[str] = None,
        status: Optional[CaseStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """查询案例列表"""
        query = {"tenant_id": tenant_id}
        if category_id:
            query["category_id"] = category_id
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
            {"_id": case_id},
            {"$inc": {"view_count": 1}}
        )

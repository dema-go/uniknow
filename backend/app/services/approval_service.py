"""审批服务"""
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.approval import Approval, ApprovalStatus


class ApprovalService:
    """审批服务类"""

    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["approvals"]
        self.cases_collection = self.db["cases"]

    async def create_approval(self, case_id: str, requester_id: str) -> Approval:
        """创建审批请求

        Args:
            case_id: 案例ID
            requester_id: 申请人ID

        Returns:
            创建的审批对象
        """
        approval_doc = {
            "case_id": case_id,
            "requester_id": requester_id,
            "status": ApprovalStatus.PENDING,
            "created_at": datetime.now(),
        }

        result = await self.collection.insert_one(approval_doc)
        approval_doc["_id"] = result.inserted_id

        return Approval(
            id=str(approval_doc["_id"]),
            case_id=approval_doc["case_id"],
            requester_id=approval_doc["requester_id"],
            status=approval_doc["status"],
            created_at=approval_doc["created_at"],
        )

    async def approve(
        self, approval_id: str, approver_id: str, comment: Optional[str] = None
    ) -> Approval:
        """审批通过

        Args:
            approval_id: 审批ID
            approver_id: 审批人ID
            comment: 审批意见

        Returns:
            更新后的审批对象
        """
        approval_oid = ObjectId(approval_id)

        update_data = {
            "status": ApprovalStatus.APPROVED,
            "approver_id": approver_id,
            "comment": comment,
            "processed_at": datetime.now(),
        }

        await self.collection.update_one(
            {"_id": approval_oid}, {"$set": update_data}
        )

        # 同时更新案例状态为已发布
        approval = await self.collection.find_one({"_id": approval_oid})
        if approval:
            await self.cases_collection.update_one(
                {"_id": ObjectId(approval["case_id"])},
                {"$set": {"status": "published"}}
            )

        return await self._get_approval(approval_oid)

    async def reject(
        self, approval_id: str, approver_id: str, comment: Optional[str] = None
    ) -> Approval:
        """审批拒绝

        Args:
            approval_id: 审批ID
            approver_id: 审批人ID
            comment: 审批意见

        Returns:
            更新后的审批对象
        """
        approval_oid = ObjectId(approval_id)

        update_data = {
            "status": ApprovalStatus.REJECTED,
            "approver_id": approver_id,
            "comment": comment,
            "processed_at": datetime.now(),
        }

        await self.collection.update_one(
            {"_id": approval_oid}, {"$set": update_data}
        )

        # 同时更新案例状态为已拒绝
        approval = await self.collection.find_one({"_id": approval_oid})
        if approval:
            await self.cases_collection.update_one(
                {"_id": ObjectId(approval["case_id"])},
                {"$set": {"status": "rejected"}}
            )

        return await self._get_approval(approval_oid)

    async def list_approvals(
        self,
        tenant_id: str,
        status: Optional[ApprovalStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[dict]:
        """获取审批列表

        Args:
            tenant_id: 租户ID
            status: 审批状态筛选
            skip: 跳过数量
            limit: 限制数量

        Returns:
            审批列表
        """
        # 构建查询条件
        query = {}
        if status:
            query["status"] = status

        # 获取审批列表
        cursor = (
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        approvals = []
        async for approval in cursor:
            # 获取关联的案例信息
            case = await self.cases_collection.find_one(
                {"_id": ObjectId(approval["case_id"])}
            )

            approvals.append(
                {
                    "id": str(approval["_id"]),
                    "case_id": approval["case_id"],
                    "case_title": case["title"] if case else "未知案例",
                    "requester_id": approval["requester_id"],
                    "requester_name": f"用户{approval['requester_id'][:8]}",
                    "approver_id": approval.get("approver_id"),
                    "approver_name": (
                        f"用户{approval.get('approver_id', '')[:8]}"
                        if approval.get("approver_id")
                        else None
                    ),
                    "status": approval["status"],
                    "comment": approval.get("comment"),
                    "created_at": approval["created_at"],
                    "processed_at": approval.get("processed_at"),
                }
            )

        return approvals

    async def get_approval_by_case(self, case_id: str) -> Optional[Approval]:
        """根据案例ID获取审批

        Args:
            case_id: 案例ID

        Returns:
            审批对象或None
        """
        approval = await self.collection.find_one({"case_id": case_id})
        if approval:
            return Approval(
                id=str(approval["_id"]),
                case_id=approval["case_id"],
                requester_id=approval["requester_id"],
                approver_id=approval.get("approver_id"),
                status=approval["status"],
                comment=approval.get("comment"),
                created_at=approval["created_at"],
                processed_at=approval.get("processed_at"),
            )
        return None

    async def _get_approval(self, approval_oid: ObjectId) -> Approval:
        """获取审批对象

        Args:
            approval_oid: 审批ObjectId

        Returns:
            审批对象
        """
        approval = await self.collection.find_one({"_id": approval_oid})
        return Approval(
            id=str(approval["_id"]),
            case_id=approval["case_id"],
            requester_id=approval["requester_id"],
            approver_id=approval.get("approver_id"),
            status=approval["status"],
            comment=approval.get("comment"),
            created_at=approval["created_at"],
            processed_at=approval.get("processed_at"),
        )

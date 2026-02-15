#!/usr/bin/env python3
"""
数据迁移脚本：将现有案例向量化并存储到 Milvus

使用方法：
    cd backend
    source .venv/bin/activate
    python scripts/migrate_to_milvus.py [--tenant-id TENANT_ID] [--batch-size BATCH_SIZE]

参数：
    --tenant-id: 指定租户 ID（默认：default）
    --batch-size: 批量处理大小（默认：10）
"""

import asyncio
import argparse
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.tools.embedding import EmbeddingService
from app.services.milvus_service import MilvusService
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.database import CaseStatus


async def migrate_cases(tenant_id: str, batch_size: int = 10):
    """迁移案例到 Milvus"""

    print(f"开始迁移案例到 Milvus...")
    print(f"租户 ID: {tenant_id}")
    print(f"批量大小: {batch_size}")
    print("-" * 50)

    # 初始化服务
    embedding_service = EmbeddingService()
    milvus_service = MilvusService()

    # 连接 Milvus
    if not milvus_service.connect():
        print("错误：无法连接到 Milvus")
        return

    # 创建集合（如果不存在）
    if not milvus_service.create_collection():
        print("错误：无法创建 Milvus 集合")
        return

    # 连接 MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]
    collection = db["cases"]

    # 查询已发布的案例
    query = {
        "tenant_id": tenant_id,
        "status": CaseStatus.PUBLISHED
    }

    total = await collection.count_documents(query)
    print(f"找到 {total} 个已发布的案例")

    if total == 0:
        print("没有需要迁移的案例")
        return

    # 批量处理
    cursor = collection.find(query)
    processed = 0
    success = 0
    failed = 0

    batch_cases = []
    batch_embeddings = []

    async for doc in cursor:
        case_id = str(doc["_id"])
        title = doc.get("title", "")
        content = doc.get("content", "")
        case_type = doc.get("case_type", "external")
        category_id = doc.get("category_id", "")

        try:
            # 生成向量
            text = f"{title}\n{content}"
            embedding = await embedding_service.embed_query(text)

            batch_cases.append({
                "case_id": case_id,
                "tenant_id": tenant_id,
                "title": title,
                "content": content,
                "embedding": embedding,
                "case_type": case_type,
                "category_id": category_id or ""
            })

            processed += 1

            # 达到批量大小时插入
            if len(batch_cases) >= batch_size:
                count = await milvus_service.batch_insert_cases(batch_cases)
                success += count
                failed += len(batch_cases) - count
                print(f"已处理: {processed}/{total}, 成功: {success}, 失败: {failed}")
                batch_cases = []

        except Exception as e:
            print(f"处理案例 {case_id} 失败: {e}")
            failed += 1
            processed += 1

    # 处理剩余的案例
    if batch_cases:
        count = await milvus_service.batch_insert_cases(batch_cases)
        success += count
        failed += len(batch_cases) - count

    print("-" * 50)
    print(f"迁移完成！")
    print(f"总计: {total}")
    print(f"成功: {success}")
    print(f"失败: {failed}")

    # 断开连接
    milvus_service.disconnect()
    client.close()


async def verify_migration(tenant_id: str):
    """验证迁移结果"""

    print(f"\n验证迁移结果...")

    # 初始化服务
    milvus_service = MilvusService()

    # 连接 Milvus
    if not milvus_service.connect():
        print("错误：无法连接到 Milvus")
        return

    collection = milvus_service.get_collection()
    if collection is None:
        print("错误：无法获取集合")
        return

    # 获取集合统计
    collection.load()
    stats = collection.num_entities
    print(f"Milvus 中的向量数量: {stats}")

    # 断开连接
    milvus_service.disconnect()


def main():
    parser = argparse.ArgumentParser(description="迁移案例到 Milvus")
    parser.add_argument(
        "--tenant-id",
        default="default",
        help="租户 ID（默认：default）"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="批量处理大小（默认：10）"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="仅验证迁移结果"
    )

    args = parser.parse_args()

    if args.verify:
        asyncio.run(verify_migration(args.tenant_id))
    else:
        asyncio.run(migrate_cases(args.tenant_id, args.batch_size))


if __name__ == "__main__":
    main()

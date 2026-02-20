"""
将 MongoDB 中的案例同步到 Milvus 向量数据库
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.tools.embedding import EmbeddingService
from app.services.milvus_service import get_milvus_service


async def sync_cases_to_milvus():
    """同步 MongoDB 中的案例到 Milvus"""
    print("开始同步案例到 Milvus...")

    # 连接 MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]
    collection = db["cases"]

    # 获取所有已发布的案例
    print("从 MongoDB 获取已发布案例...")
    cursor = collection.find({"status": "published"})
    cases = await cursor.to_list(length=1000)
    print(f"找到 {len(cases)} 个已发布案例")

    if not cases:
        print("没有需要同步的案例")
        return

    # 获取 Milvus 服务
    milvus_service = get_milvus_service()
    if milvus_service is None:
        print("Milvus 服务初始化失败")
        return

    # 获取 Embedding 服务
    embedding_service = EmbeddingService()

    # 同步每个案例
    success_count = 0
    error_count = 0

    for case in cases:
        case_id = str(case.get("_id"))
        tenant_id = case.get("tenant_id", "default_tenant")
        title = case.get("title", "")
        content = case.get("content", "")

        # 跳过文档类型的案例（没有 content）
        if case.get("case_form") == "document":
            print(f"跳过文档类型案例: {case_id} - {title}")
            continue

        try:
            # 生成 embedding
            text = f"{title}\n{content}" if content else title
            embeddings = await embedding_service.embed_documents([text])
            embedding = embeddings[0]

            # 插入 Milvus
            result = await milvus_service.insert_case(
                case_id=case_id,
                tenant_id=tenant_id,
                title=title,
                content=content[:8000] if content else "",
                embedding=embedding,
                case_type=case.get("case_type", "external"),
                category_id=str(case.get("category_id", ""))
            )

            if result:
                success_count += 1
                print(f"✓ 同步成功: {case_id} - {title[:30]}")
            else:
                error_count += 1
                print(f"✗ 同步失败: {case_id} - {title[:30]}")

        except Exception as e:
            error_count += 1
            print(f"✗ 同步出错: {case_id} - {title[:30]}: {e}")

    print(f"\n同步完成: 成功 {success_count}, 失败 {error_count}")

    # 验证
    print("\n验证 Milvus 数据...")
    from pymilvus import connections, Collection

    connections.connect(
        alias="default",
        host="localhost",
        port="19530"
    )
    collection = Collection("cases")
    collection.load()
    print(f"Milvus 中共有 {collection.num_entities} 条向量数据")

    connections.disconnect("default")


if __name__ == "__main__":
    asyncio.run(sync_cases_to_milvus())

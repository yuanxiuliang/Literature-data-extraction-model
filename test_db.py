"""
数据库测试脚本

测试数据库连接和基本功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_session
from app.services.paper_service import PaperService
from app.services.crystal_material_service import CrystalMaterialService
from app.services.growth_method_service import GrowthMethodService
from app.models.growth_methods import MethodType

def test_database():
    """测试数据库功能"""
    print("🧪 开始测试数据库功能...")
    
    # 获取数据库会话
    db = next(get_session())
    
    try:
        # 测试文献服务
        print("\n📄 测试文献服务...")
        paper_service = PaperService()
        
        # 创建测试文献
        paper = paper_service.create_or_get_by_doi(db, "10.1000/test.doi")
        print(f"✅ 创建文献: {paper}")
        
        # 测试晶体材料服务
        print("\n🔬 测试晶体材料服务...")
        material_service = CrystalMaterialService()
        
        # 创建测试材料
        material = material_service.create_or_get_by_formula(
            db, 
            "SiO2", 
            crystal_system="六方",
            space_group="P6_322"
        )
        print(f"✅ 创建材料: {material}")
        
        # 测试生长方法服务
        print("\n⚗️ 测试生长方法服务...")
        method_service = GrowthMethodService()
        
        # 创建测试生长方法
        growth_method = method_service.create_growth_method(
            db,
            paper_id=paper.id,
            material_id=material.id,
            method_type=MethodType.FLUX_METHOD
        )
        print(f"✅ 创建生长方法: {growth_method}")
        
        # 测试查询功能
        print("\n🔍 测试查询功能...")
        
        # 查询所有文献
        papers = paper_service.get_all(db)
        print(f"📚 文献总数: {len(papers)}")
        
        # 查询所有材料
        materials = material_service.get_all(db)
        print(f"🧪 材料总数: {len(materials)}")
        
        # 查询所有生长方法
        methods = method_service.get_all(db)
        print(f"⚗️ 生长方法总数: {len(methods)}")
        
        print("\n✅ 数据库测试完成！所有功能正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_database()

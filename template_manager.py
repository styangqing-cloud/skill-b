"""
模板管理模块

该模块提供模板管理功能,包括模板版本管理、快速应用、自定义等功能。

作者: tommyyang@tencent
版本: 3.0.0
更新时间: 2026-03-14
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
from enum import Enum


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 枚举定义 ====================

class TemplateType(Enum):
    """模板类型枚举"""
    PRESET = "preset"  # 预设模板
    CUSTOM = "custom"  # 自定义模板


class TemplateStatus(Enum):
    """模板状态枚举"""
    ACTIVE = "active"  # 激活
    ARCHIVED = "archived"  # 归档
    DRAFT = "draft"  # 草稿


# ==================== 数据模型 ====================

@dataclass
class Template:
    """模板数据模型"""
    id: str  # 模板ID
    name: str  # 模板名称
    type: TemplateType  # 模板类型
    status: TemplateStatus  # 模板状态
    interview_type: str  # 访谈类型
    level_range: str  # 职级范围
    
    # 模板内容
    opening: str  # 开场环节
    core_questions: List[str]  # 核心问题
    sensitive_questions: List[str]  # 敏感问题
    closing: str  # 总结环节
    
    # 元数据
    version: str  # 版本号
    created_at: str  # 创建时间
    updated_at: str  # 更新时间
    created_by: str  # 创建者
    description: Optional[str] = None  # 模板描述
    tags: Optional[List[str]] = None  # 标签
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """从字典创建"""
        data['type'] = TemplateType(data['type'])
        data['status'] = TemplateStatus(data['status'])
        return cls(**data)


@dataclass
class TemplateVersion:
    """模板版本数据模型"""
    template_id: str  # 模板ID
    version: str  # 版本号
    content: str  # 模板内容(Markdown格式)
    created_at: str  # 创建时间
    created_by: str  # 创建者
    change_log: Optional[str] = None  # 变更日志
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


# ==================== 模板管理器 ====================

class TemplateManager:
    """
    模板管理器类
    
    提供以下功能:
    - 模板的创建、读取、更新、删除
    - 模板版本管理
    - 模板快速应用
    - 模板搜索和过滤
    """
    
    def __init__(self, storage_path: str = "templates/"):
        """
        初始化模板管理器
        
        Args:
            storage_path: 模板存储路径
        """
        self.storage_path = storage_path
        self.templates: Dict[str, Template] = {}
        self.template_versions: Dict[str, List[TemplateVersion]] = {}
        self.max_versions = 5  # 最大保留版本数
        
        # 创建存储目录
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "versions"), exist_ok=True)
        
        # 加载现有模板
        self._load_templates()
    
    def _generate_template_id(self, name: str) -> str:
        """
        生成模板ID
        
        Args:
            name: 模板名称
            
        Returns:
            模板ID
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        content = f"{name}{timestamp}"
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:16]
    
    def _load_templates(self) -> None:
        """加载现有模板"""
        # 加载模板元数据
        metadata_file = os.path.join(self.storage_path, "metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for template_data in data:
                        template = Template.from_dict(template_data)
                        self.templates[template.id] = template
                        logger.info(f"加载模板: {template.name} ({template.id})")
            except Exception as e:
                logger.error(f"加载模板元数据失败: {e}")
        
        # 加载模板版本
        versions_file = os.path.join(self.storage_path, "versions.json")
        if os.path.exists(versions_file):
            try:
                with open(versions_file, 'r', encoding='utf-8') as f:
                    versions_data = json.load(f)
                    for template_id, version_list in versions_data.items():
                        self.template_versions[template_id] = [
                            TemplateVersion(**v) for v in version_list
                        ]
            except Exception as e:
                logger.error(f"加载模板版本失败: {e}")
    
    def _save_templates(self) -> None:
        """保存模板元数据"""
        metadata_file = os.path.join(self.storage_path, "metadata.json")
        try:
            data = [template.to_dict() for template in self.templates.values()]
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存模板元数据失败: {e}")
            raise
    
    def _save_template_versions(self) -> None:
        """保存模板版本"""
        versions_file = os.path.join(self.storage_path, "versions.json")
        try:
            versions_data = {}
            for template_id, versions in self.template_versions.items():
                versions_data[template_id] = [v.to_dict() for v in versions]
            with open(versions_file, 'w', encoding='utf-8') as f:
                json.dump(versions_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存模板版本失败: {e}")
            raise
    
    def create_template(
        self,
        name: str,
        interview_type: str,
        level_range: str,
        opening: str,
        core_questions: List[str],
        sensitive_questions: List[str],
        closing: str,
        created_by: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        template_type: TemplateType = TemplateType.CUSTOM
    ) -> Template:
        """
        创建新模板
        
        Args:
            name: 模板名称
            interview_type: 访谈类型
            level_range: 职级范围
            opening: 开场环节
            core_questions: 核心问题
            sensitive_questions: 敏感问题
            closing: 总结环节
            created_by: 创建者
            description: 模板描述
            tags: 标签
            template_type: 模板类型
            
        Returns:
            创建的模板
        """
        # 生成模板ID
        template_id = self._generate_template_id(name)
        
        # 创建模板
        template = Template(
            id=template_id,
            name=name,
            type=template_type,
            status=TemplateStatus.ACTIVE,
            interview_type=interview_type,
            level_range=level_range,
            opening=opening,
            core_questions=core_questions,
            sensitive_questions=sensitive_questions,
            closing=closing,
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            created_by=created_by,
            description=description,
            tags=tags or []
        )
        
        # 保存模板
        self.templates[template_id] = template
        
        # 创建初始版本
        content = self._template_to_markdown(template)
        version = TemplateVersion(
            template_id=template_id,
            version="1.0.0",
            content=content,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            change_log="初始版本"
        )
        self.template_versions[template_id] = [version]
        
        # 持久化
        self._save_templates()
        self._save_template_versions()
        
        logger.info(f"创建模板: {name} ({template_id})")
        return template
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """
        获取模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板对象,如果不存在则返回None
        """
        return self.templates.get(template_id)
    
    def get_template_by_name(self, name: str) -> Optional[Template]:
        """
        根据名称获取模板
        
        Args:
            name: 模板名称
            
        Returns:
            模板对象,如果不存在则返回None
        """
        for template in self.templates.values():
            if template.name == name:
                return template
        return None
    
    def search_templates(
        self,
        interview_type: Optional[str] = None,
        level_range: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[TemplateStatus] = None
    ) -> List[Template]:
        """
        搜索模板
        
        Args:
            interview_type: 访谈类型(可选)
            level_range: 职级范围(可选)
            tags: 标签列表(可选)
            status: 模板状态(可选)
            
        Returns:
            匹配的模板列表
        """
        results = []
        
        for template in self.templates.values():
            # 过滤访谈类型
            if interview_type and template.interview_type != interview_type:
                continue
            
            # 过滤职级范围
            if level_range and template.level_range != level_range:
                continue
            
            # 过滤状态
            if status and template.status != status:
                continue
            
            # 过滤标签
            if tags:
                if not all(tag in (template.tags or []) for tag in tags):
                    continue
            
            results.append(template)
        
        return results
    
    def update_template(
        self,
        template_id: str,
        opening: Optional[str] = None,
        core_questions: Optional[List[str]] = None,
        sensitive_questions: Optional[List[str]] = None,
        closing: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        updated_by: str = "",
        change_log: Optional[str] = None
    ) -> Optional[Template]:
        """
        更新模板
        
        Args:
            template_id: 模板ID
            opening: 开场环节(可选)
            core_questions: 核心问题(可选)
            sensitive_questions: 敏感问题(可选)
            closing: 总结环节(可选)
            description: 模板描述(可选)
            tags: 标签(可选)
            updated_by: 更新者
            change_log: 变更日志
            
        Returns:
            更新后的模板,如果不存在则返回None
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        # 保存旧版本
        old_version_content = self._template_to_markdown(template)
        old_version = template.version
        
        # 更新字段
        if opening is not None:
            template.opening = opening
        if core_questions is not None:
            template.core_questions = core_questions
        if sensitive_questions is not None:
            template.sensitive_questions = sensitive_questions
        if closing is not None:
            template.closing = closing
        if description is not None:
            template.description = description
        if tags is not None:
            template.tags = tags
        
        template.updated_at = datetime.now().isoformat()
        
        # 生成新版本号
        major, minor, patch = old_version.split('.')
        template.version = f"{major}.{minor}.{int(patch) + 1}"
        
        # 保存更新后的模板
        self.templates[template_id] = template
        
        # 创建新版本记录
        new_version_content = self._template_to_markdown(template)
        version = TemplateVersion(
            template_id=template_id,
            version=template.version,
            content=new_version_content,
            created_at=datetime.now().isoformat(),
            created_by=updated_by,
            change_log=change_log or "更新模板"
        )
        
        # 添加版本历史
        if template_id not in self.template_versions:
            self.template_versions[template_id] = []
        self.template_versions[template_id].append(version)
        
        # 限制版本数量
        if len(self.template_versions[template_id]) > self.max_versions:
            self.template_versions[template_id] = self.template_versions[template_id][-self.max_versions:]
        
        # 持久化
        self._save_templates()
        self._save_template_versions()
        
        logger.info(f"更新模板: {template.name} (v{template.version})")
        return template
    
    def delete_template(self, template_id: str) -> bool:
        """
        删除模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            是否删除成功
        """
        if template_id not in self.templates:
            return False
        
        del self.templates[template_id]
        
        if template_id in self.template_versions:
            del self.template_versions[template_id]
        
        self._save_templates()
        self._save_template_versions()
        
        logger.info(f"删除模板: {template_id}")
        return True
    
    def get_template_versions(self, template_id: str) -> List[TemplateVersion]:
        """
        获取模板版本历史
        
        Args:
            template_id: 模板ID
            
        Returns:
            版本历史列表
        """
        return self.template_versions.get(template_id, [])
    
    def get_template_version(self, template_id: str, version: str) -> Optional[TemplateVersion]:
        """
        获取特定版本的模板
        
        Args:
            template_id: 模板ID
            version: 版本号
            
        Returns:
            模板版本,如果不存在则返回None
        """
        versions = self.get_template_versions(template_id)
        for v in versions:
            if v.version == version:
                return v
        return None
    
    def apply_template(
        self,
        template_id: str,
        employee_info: Dict[str, Any]
    ) -> str:
        """
        应用模板生成提纲
        
        Args:
            template_id: 模板ID
            employee_info: 员工信息
            
        Returns:
            生成的提纲(Markdown格式)
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")
        
        # 替换模板中的占位符
        outline = self._template_to_markdown(template, employee_info)
        
        logger.info(f"应用模板: {template.name} ({template_id})")
        return outline
    
    def _template_to_markdown(
        self,
        template: Template,
        employee_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        将模板转换为Markdown格式
        
        Args:
            template: 模板对象
            employee_info: 员工信息(可选,用于替换占位符)
            
        Returns:
            Markdown格式的内容
        """
        md_content = f"# {template.name}\n\n"
        
        if template.description:
            md_content += f"> {template.description}\n\n"
        
        if template.tags:
            tags_str = " ".join([f"#{tag}" for tag in template.tags])
            md_content += f"**标签**: {tags_str}\n\n"
        
        md_content += f"**访谈类型**: {template.interview_type}\n"
        md_content += f"**职级范围**: {template.level_range}\n"
        md_content += f"**版本**: {template.version}\n"
        md_content += f"**更新时间**: {template.updated_at}\n\n"
        
        md_content += "---\n\n"
        md_content += template.opening
        
        for i, question in enumerate(template.core_questions, 1):
            md_content += f"\n### 核心问题 {i}\n"
            md_content += question
        
        if template.sensitive_questions:
            md_content += "\n---\n\n"
            md_content += "## 敏感问题\n\n"
            for i, question in enumerate(template.sensitive_questions, 1):
                md_content += f"\n### 敏感问题 {i}\n"
                md_content += question
        
        md_content += "\n---\n\n"
        md_content += template.closing
        
        # 替换占位符
        if employee_info:
            md_content = self._replace_placeholders(md_content, employee_info)
        
        return md_content
    
    def _replace_placeholders(
        self,
        content: str,
        employee_info: Dict[str, Any]
    ) -> str:
        """
        替换内容中的占位符
        
        Args:
            content: 原始内容
            employee_info: 员工信息
            
        Returns:
            替换后的内容
        """
        replacements = {
            "{name}": employee_info.get("name", ""),
            "{position}": employee_info.get("position", ""),
            "{department}": employee_info.get("department", ""),
            "{hire_date}": employee_info.get("hire_date", ""),
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content
    
    def list_templates(
        self,
        status: Optional[TemplateStatus] = None
    ) -> List[Template]:
        """
        列出所有模板
        
        Args:
            status: 模板状态(可选)
            
        Returns:
            模板列表
        """
        templates = list(self.templates.values())
        
        if status:
            templates = [t for t in templates if t.status == status]
        
        return templates


# ==================== 工厂类 ====================

class TemplateManagerFactory:
    """模板管理器工厂类"""
    
    @staticmethod
    def create_manager(storage_path: str = "templates/") -> TemplateManager:
        """
        创建模板管理器实例
        
        Args:
            storage_path: 模板存储路径
            
        Returns:
            模板管理器实例
        """
        return TemplateManager(storage_path=storage_path)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例1: 创建模板管理器
    manager = TemplateManagerFactory.create_manager()
    
    # 示例2: 创建模板
    template = manager.create_template(
        name="P8离职访谈模板",
        interview_type="离职访谈",
        level_range="P8-P9",
        opening="## 开场环节\n感谢你抽出时间...",
        core_questions=["问题1", "问题2"],
        sensitive_questions=["敏感问题1"],
        closing="## 总结\n祝你前程似锦...",
        created_by="hr_user",
        description="针对P8高绩效员工的离职访谈模板",
        tags=["离职", "P8", "高绩效"]
    )
    
    print(f"创建模板: {template.name} (ID: {template.id})")
    
    # 示例3: 搜索模板
    results = manager.search_templates(
        interview_type="离职访谈",
        level_range="P8-P9"
    )
    print(f"搜索结果: {len(results)} 个模板")
    
    # 示例4: 应用模板
    employee_info = {
        "name": "张三",
        "position": "P8 高级产品策划",
        "department": "产品部",
        "hire_date": "2020-01-01"
    }
    outline = manager.apply_template(template.id, employee_info)
    print(f"生成的提纲长度: {len(outline)} 字符")

"""
员工访谈提纲生成器 - 核心逻辑模块

该模块实现了员工访谈提纲生成的核心工作流程,
包括强制校验、信息提取、提纲生成等功能。

作者: tommyyang@tencent
版本: 3.0.0
更新时间: 2026-03-14
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


# ==================== 枚举定义 ====================

class InterviewType(Enum):
    """访谈类型枚举"""
    ENTRY = "入职访谈"
    PERFORMANCE = "绩效访谈"
    RESIGNATION = "离职访谈"
    PROMOTION = "晋升访谈"
    CAREER_DEVELOPMENT = "职业发展"
    TEAM_FEEDBACK = "团队反馈"
    RETENTION = "挽留访谈"
    TRANSFER = "转岗访谈"
    ORGANIZATION_DIAGNOSIS = "组织诊断访谈"


class ResignationType(Enum):
    """离职类型枚举"""
    ACTIVE = "主动离职"
    PASSIVE = "被动离职"


class PerformanceLevel(Enum):
    """绩效等级枚举"""
    OUTSTANDING = "Outstanding"
    GOOD = "Good"
    SATISFACTORY = "Satisfactory"
    UNDERPERFORM = "Underperform"


# ==================== 数据模型 ====================

@dataclass
class EmployeeInfo:
    """员工信息数据模型"""
    name: str  # 姓名
    position: str  # 职位/职级
    department: str  # 部门
    hire_date: str  # 入职时间
    tenure_months: int  # 入职时长(月)
    
    # 绩效相关
    performance_history: List[PerformanceLevel]  # 绩效历史
    recent_performance: PerformanceLevel  # 最近绩效
    
    # 项目和能力
    core_projects: List[str]  # 核心项目
    capabilities: List[str]  # 能力特长
    achievements: List[str]  # 主要成就
    
    # 离职相关(可选)
    resignation_type: Optional[ResignationType] = None
    estimated_reason: Optional[str] = None  # 估计的离职原因


@dataclass
class InterviewStrategy:
    """访谈策略数据模型"""
    key_points: List[str]  # 关键点
    approach: str  # 策略方法
    precautions: List[str]  # 注意事项
    methodology: str  # 使用的方法论


@dataclass
class InterviewOutline:
    """访谈提纲数据模型"""
    employee_info: EmployeeInfo  # 员工信息
    interview_type: InterviewType  # 访谈类型
    purpose: str  # 访谈目的
    strategy: InterviewStrategy  # 访谈策略
    
    # 提纲内容
    opening: str  # 开场环节
    core_questions: List[str]  # 核心问题
    sensitive_questions: List[str]  # 敏感问题
    closing: str  # 总结环节
    
    # 元数据
    duration_minutes: int  # 预计时长
    methodology: str  # 使用的方法论


# ==================== 异常定义 ====================

class InterviewGeneratorError(Exception):
    """基础异常类"""
    def __init__(self, code: str, message: str, suggestion: str = None):
        self.code = code
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def __str__(self):
        result = f"[{self.code}] {self.message}"
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        return result


class HardGateError(InterviewGeneratorError):
    """强制校验失败异常"""
    pass


class FileProcessingError(InterviewGeneratorError):
    """文件处理失败异常"""
    pass


class ValidationLevel(Enum):
    """校验级别"""
    REQUIRED = "必填"  # 必须提供
    RECOMMENDED = "建议"  # 建议提供
    OPTIONAL = "可选"  # 可选


# ==================== 核心类定义 ====================

class InterviewGenerator:
    """
    员工访谈提纲生成器核心类
    
    该类实现了完整的访谈提纲生成工作流程:
    1. 强制校验(HARD-GATE)
    2. 信息提取
    3. 访谈策略生成
    4. 访谈提纲生成
    """
    
    # 强制校验字段
    HARD_GATE_REQUIRED = {
        "interview_type": (ValidationLevel.REQUIRED, "访谈类型"),
        "position": (ValidationLevel.REQUIRED, "员工职级/职位"),
        "purpose": (ValidationLevel.REQUIRED, "访谈目的")
    }
    
    # 访谈类型到方法论的映射
    INTERVIEW_METHODOLOGY_MAP = {
        InterviewType.ENTRY: "基础方法",
        InterviewType.PERFORMANCE: "BEM模型",
        InterviewType.RESIGNATION: "推拉力理论",
        InterviewType.PROMOTION: "能力评估模型",
        InterviewType.CAREER_DEVELOPMENT: "职业锚+GROW模型",
        InterviewType.TEAM_FEEDBACK: "团队诊断方法",
        InterviewType.RETENTION: "推拉力理论",
        InterviewType.TRANSFER: "职业锚理论",
        InterviewType.ORGANIZATION_DIAGNOSIS: "六盒模型"
    }
    
    # 访谈时长配置(分钟)
    INTERVIEW_DURATION_MAP = {
        InterviewType.ENTRY: 30,
        InterviewType.PERFORMANCE: 45,
        InterviewType.RESIGNATION: 60,
        InterviewType.PROMOTION: 60,
        InterviewType.CAREER_DEVELOPMENT: 45,
        InterviewType.TEAM_FEEDBACK: 30,
        InterviewType.RETENTION: 60,
        InterviewType.TRANSFER: 30,
        InterviewType.ORGANIZATION_DIAGNOSIS: 90
    }
    
    # 绩效分析权重
    PERFORMANCE_WEIGHTS = {
        "recent_1": 0.7,  # 最近1次绩效权重70%
        "recent_2": 0.3   # 最近2次绩效权重30%
    }
    
    def __init__(self):
        """初始化生成器"""
        self.employee_info: Optional[EmployeeInfo] = None
        self.interview_type: Optional[InterviewType] = None
        self.purpose: str = ""
    
    def validate_hard_gate(self, employee_info_dict: Dict) -> Tuple[bool, List[str]]:
        """
        强制校验核心信息(HARD-GATE)
        
        Args:
            employee_info_dict: 员工信息字典
            
        Returns:
            (是否通过校验, 缺失字段列表)
        """
        missing_fields = []
        
        for field, (level, field_name) in self.HARD_GATE_REQUIRED.items():
            if level == ValidationLevel.REQUIRED:
                if field not in employee_info_dict or not employee_info_dict[field]:
                    missing_fields.append(field_name)
        
        return len(missing_fields) == 0, missing_fields
    
    def analyze_performance_trend(self, performance_history: List[PerformanceLevel]) -> str:
        """
        分析绩效趋势
        
        Args:
            performance_history: 绩效历史
            
        Returns:
            绩效趋势描述
        """
        if len(performance_history) < 2:
            return "绩效数据不足"
        
        # 获取最近两次绩效
        recent_2 = performance_history[-2]
        recent_1 = performance_history[-1]
        
        # 定义绩效等级权重
        performance_weights = {
            PerformanceLevel.OUTSTANDING: 4,
            PerformanceLevel.GOOD: 3,
            PerformanceLevel.SATISFACTORY: 2,
            PerformanceLevel.UNDERPERFORM: 1
        }
        
        weight_2 = performance_weights.get(recent_2, 0)
        weight_1 = performance_weights.get(recent_1, 0)
        
        # 计算趋势
        if weight_1 > weight_2:
            return "上升期 - 绩效持续提升"
        elif weight_1 < weight_2:
            return "下降期 - 绩效有所下滑"
        elif weight_1 >= 3:
            return "稳定高绩效 - 持续优秀表现"
        else:
            return "稳定中等绩效 - 表现平稳"
    
    def select_methodology(self, interview_type: InterviewType) -> str:
        """
        根据访谈类型选择方法论
        
        Args:
            interview_type: 访谈类型
            
        Returns:
            方法论名称
        """
        return self.INTERVIEW_METHODOLOGY_MAP.get(
            interview_type, 
            "通用方法"
        )
    
    def generate_strategy(
        self, 
        employee_info: EmployeeInfo, 
        interview_type: InterviewType,
        purpose: str
    ) -> InterviewStrategy:
        """
        生成访谈策略
        
        Args:
            employee_info: 员工信息
            interview_type: 访谈类型
            purpose: 访谈目的
            
        Returns:
            访谈策略
        """
        # 选择方法论
        methodology = self.select_methodology(interview_type)
        
        # 分析绩效趋势
        performance_trend = self.analyze_performance_trend(employee_info.performance_history)
        
        # 生成关键点
        key_points = [
            f"方法论: {methodology}",
            f"绩效趋势: {performance_trend}",
            f"职级策略: 根据员工职级调整问题深度"
        ]
        
        # 生成策略方法
        if interview_type == InterviewType.RESIGNATION:
            if employee_info.resignation_type == ResignationType.ACTIVE:
                approach = "采用'共情+探究+开放'的三段式策略,基于推拉力理论分析离职驱动力"
            else:
                approach = "采用'理解+支持+规划'的策略,关注员工情绪和未来发展"
        elif interview_type == InterviewType.PERFORMANCE:
            approach = "采用'回顾+评估+改进'的策略,基于BEM模型分析绩效影响因素"
        elif interview_type == InterviewType.CAREER_DEVELOPMENT:
            approach = "采用'目标+现状+选择+行动'的GROW模型,结合职业锚理论识别发展方向"
        else:
            approach = f"采用{methodology}设计访谈流程,确保问题设计科学、逻辑清晰"
        
        # 生成注意事项
        precautions = [
            "营造安全对话氛围,降低心理防御",
            "保持尊重和开放的态度,避免评价或争辩",
            "记录所有建设性建议,为组织改进提供输入"
        ]
        
        if interview_type == InterviewType.RESIGNATION:
            precautions.extend([
                "避免直接追问离职细节,侧面了解真实原因",
                "对高绩效员工保持尊重,避免'挽留式施压'",
                "准备应对薪酬福利等敏感话题,预设弹性空间"
            ])
        
        return InterviewStrategy(
            key_points=key_points,
            approach=approach,
            precautions=precautions,
            methodology=methodology
        )
    
    def generate_outline(
        self,
        employee_info: EmployeeInfo,
        interview_type: InterviewType,
        purpose: str,
        strategy: InterviewStrategy
    ) -> InterviewOutline:
        """
        生成访谈提纲
        
        Args:
            employee_info: 员工信息
            interview_type: 访谈类型
            purpose: 访谈目的
            strategy: 访谈策略
            
        Returns:
            访谈提纲
        """
        # 获取访谈时长
        duration = self.INTERVIEW_DURATION_MAP.get(interview_type, 60)
        
        # 生成开场环节
        opening = self._generate_opening(employee_info, interview_type, purpose)
        
        # 生成核心问题
        core_questions = self._generate_core_questions(
            employee_info, interview_type, purpose
        )
        
        # 生成敏感问题
        sensitive_questions = self._generate_sensitive_questions(
            employee_info, interview_type
        )
        
        # 生成总结环节
        closing = self._generate_closing(interview_type)
        
        return InterviewOutline(
            employee_info=employee_info,
            interview_type=interview_type,
            purpose=purpose,
            strategy=strategy,
            opening=opening,
            core_questions=core_questions,
            sensitive_questions=sensitive_questions,
            closing=closing,
            duration_minutes=duration,
            methodology=strategy.methodology
        )
    
    def _generate_opening(
        self,
        employee_info: EmployeeInfo,
        interview_type: InterviewType,
        purpose: str
    ) -> str:
        """生成开场环节"""
        if interview_type == InterviewType.RESIGNATION:
            return f"""
## 开场环节 (5-10分钟)

### 1. 破冰与目的说明
- "感谢你抽出时间进行这次面谈"
- "今天的面谈主要是{purpose}"
- "我们的对话完全保密,目的是帮助你顺利完成离职,同时让公司获得改进的机会"

### 2. 情绪确认
- "你现在心情如何?对这个决定是否还有犹豫?"
- "家人和朋友对这个决定的态度是怎样的?"
"""
        else:
            return f"""
## 开场环节 (5-10分钟)

### 1. 欢迎与目的说明
- "感谢你抽出时间进行这次面谈"
- "今天的面谈主要是{purpose}"

### 2. 情绪确认
- "你现在的状态如何?有没有什么特别想分享的?"
"""
    
    def _generate_core_questions(
        self,
        employee_info: EmployeeInfo,
        interview_type: InterviewType,
        purpose: str
    ) -> List[str]:
        """生成核心问题"""
        if interview_type == InterviewType.RESIGNATION:
            return [
                """
## 核心问题 (25-35分钟)

### 离职决策过程
**推力分析(现有工作负面因素)**:
- "是什么触发了你开始考虑其他机会的想法?"
- "在过去一年中,有没有哪些时刻或事件让你感到特别失望或受挫?"
- "在工作中遇到的最大挑战是什么?"

**拉力分析(外部机会吸引力)**:
- "你理想中的下一份工作或职业方向是怎样的?"
- "外部的机会中最吸引你的是什么?"
- "如果公司能提供类似的资源或机会,你觉得还有可能 reconsider 吗?"

**留任力评估**:
- "在公司这几年,有哪些经历或成就是你最珍视的?"
- "公司和团队中,有哪些人是你特别舍不得离开的?"

**移动障碍**:
- "做出这个决定过程中,你最大的顾虑是什么?"
""",
                """
### 工作体验与团队反馈
**工作内容与成就感**:
- "在你负责的产品/项目中,最有成就感的是什么?"
- "你认为你的哪些优势得到了充分发挥?"

**团队协作与文化**:
- "你如何评价团队的工作氛围和协作效率?"
- "与上级、平级、跨部门合作的体验如何?"
""",
                """
### 职业发展与成长
**短期与长期目标**:
- "你未来3-5年的职业规划是怎样的?"
- "公司提供的职业发展路径是否符合你的预期?"

**能力提升与学习机会**:
- "在公司期间,哪些学习机会对你帮助最大?"
- "公司是否提供了足够的学习资源和培训机会?"
"""
            ]
        else:
            return [
                """
## 核心问题 (25-35分钟)

### 工作回顾
- "请回顾一下最近一段时间的工作,你最大的收获是什么?"
- "在工作中遇到的挑战是什么?你是如何克服的?"
""",
                """
### 能力与成长
- "你认为自己在哪些方面得到了提升?"
- "还有哪些能力或经验是你希望进一步发展的?"
"""
            ]
    
    def _generate_sensitive_questions(
        self,
        employee_info: EmployeeInfo,
        interview_type: InterviewType
    ) -> List[str]:
        """生成敏感问题"""
        if interview_type == InterviewType.RESIGNATION:
            return [
                """
## 敏感问题 (15-20分钟)

### 薪酬福利(谨慎处理)
**间接询问**:
- "你对自己当前的薪酬福利待遇整体评价如何?"
- "外部的offer在薪酬方面相比目前有多大的差异?"
- "除了薪酬,还有哪些福利或激励措施是你比较在意的?"

**挽留试探**(如果仍有挽留空间):
- "如果公司能在某些方面提供更有竞争力的条件,你愿意重新考虑吗?"
""",
                """
### 上级与公司层面
**向上管理体验**:
- "你与直属领导的沟通顺畅吗?"
- "你希望领导在哪些方面给你更多支持?"

**组织与流程**:
- "公司的决策效率、流程设计等方面,哪些让你感到困扰?"
- "跨部门协作中最大的痛点是什么?"
"""
            ]
        else:
            return [
                """
## 敏感问题 (15-20分钟)

### 潜在挑战
- "在工作中,有哪些是你感到特别困难或压力较大的地方?"
- "有没有什么是你觉得需要改进的?"
"""
            ]
    
    def _generate_closing(self, interview_type: InterviewType) -> str:
        """生成总结环节"""
        return """
## 总结与结束 (5-10分钟)

### 建设性反馈与改进建议
- "如果让你给公司提3条改进建议,你会说什么?"
- "公司如何才能更好地留住高绩效人才?"

### 关系维护与未来可能
- "我们非常珍视你的专业能力,希望离职后我们还能保持联系"
- "你愿意保持联系方式吗?"

### 祝福与结束
- "再次感谢你的坦诚分享,你的反馈对我们非常重要"
- "祝愿你在新的工作岗位上取得更大的成就!"
"""
    
    def to_markdown(self, outline: InterviewOutline) -> str:
        """
        将提纲转换为Markdown格式
        
        Args:
            outline: 访谈提纲
            
        Returns:
            Markdown格式的提纲
        """
        md_content = f"""# {outline.employee_info.position} 访谈提纲

## 一、访谈策略

**重点策略**:
{outline.strategy.approach}

**关键点**:
"""
        for point in outline.strategy.key_points:
            md_content += f"- {point}\n"
        
        md_content += f"\n**注意事项**:\n"
        for precaution in outline.strategy.precautions:
            md_content += f"- {precaution}\n"
        
        md_content += f"\n**预计时长**: {outline.duration_minutes} 分钟\n"
        md_content += f"**使用方法论**: {outline.methodology}\n"
        
        md_content += f"\n{outline.opening}"
        
        for questions in outline.core_questions:
            md_content += f"\n{questions}"
        
        for questions in outline.sensitive_questions:
            md_content += f"\n{questions}"
        
        md_content += f"\n{outline.closing}"
        
        md_content += f"\n---\n\n**生成时间**: {self._get_current_time()}\n"
        md_content += f"**适用对象**: {outline.employee_info.name} ({outline.employee_info.position})\n"
        
        return md_content
    
    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ==================== 工厂类 ====================

class InterviewGeneratorFactory:
    """访谈生成器工厂类"""
    
    @staticmethod
    def create_generator(interview_type: InterviewType) -> InterviewGenerator:
        """
        创建生成器实例
        
        Args:
            interview_type: 访谈类型
            
        Returns:
            生成器实例
        """
        return InterviewGenerator()
    
    @staticmethod
    def create_from_dict(employee_info_dict: Dict) -> InterviewGenerator:
        """
        从字典创建生成器并初始化
        
        Args:
            employee_info_dict: 员工信息字典
            
        Returns:
            已初始化的生成器实例
            
        Raises:
            HardGateError: 强制校验失败
        """
        generator = InterviewGenerator()
        
        # 强制校验
        passed, missing = generator.validate_hard_gate(employee_info_dict)
        if not passed:
            raise HardGateError(
                code="HARD_GATE_001",
                message=f"缺少核心信息: {', '.join(missing)}",
                suggestion="请提供访谈类型、员工职级和访谈目的"
            )
        
        return generator


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例1: 创建生成器
    generator = InterviewGenerator()
    
    # 示例2: 强制校验
    employee_info_dict = {
        "interview_type": "离职访谈",
        "position": "P8 高级产品策划",
        "purpose": "了解真实离职原因,评估挽留可能性"
    }
    
    try:
        passed, missing = generator.validate_hard_gate(employee_info_dict)
        if not passed:
            print(f"校验失败,缺少: {missing}")
    except HardGateError as e:
        print(f"错误: {e}")
    
    # 示例3: 绩效分析
    performance_history = [
        PerformanceLevel.GOOD,
        PerformanceLevel.OUTSTANDING
    ]
    trend = generator.analyze_performance_trend(performance_history)
    print(f"绩效趋势: {trend}")
    
    # 示例4: 选择方法论
    methodology = generator.select_methodology(InterviewType.RESIGNATION)
    print(f"方法论: {methodology}")

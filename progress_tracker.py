"""
进度跟踪模块

该模块提供进度跟踪功能,包括实时进度显示、完成率提示、状态更新等。

作者: tommyyang@tencent
版本: 3.0.0
更新时间: 2026-03-14
"""

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 枚举定义 ====================

class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = "pending"  # 待处理
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    SKIPPED = "skipped"  # 跳过


# ==================== 数据模型 ====================

@dataclass
class WorkflowStep:
    """工作流步骤数据模型"""
    id: str  # 步骤ID
    name: str  # 步骤名称
    description: str  # 步骤描述
    status: StepStatus  # 状态
    order: int  # 执行顺序
    
    # 时间信息
    started_at: Optional[str] = None  # 开始时间
    completed_at: Optional[str] = None  # 完成时间
    duration_seconds: Optional[float] = None  # 持续时间(秒)
    
    # 错误信息
    error_message: Optional[str] = None  # 错误消息
    error_details: Optional[str] = None  # 错误详情
    
    # 进度信息
    progress_percent: float = 0.0  # 进度百分比(0-100)
    sub_steps: Optional[List['WorkflowStep']] = None  # 子步骤


@dataclass
class WorkflowProgress:
    """工作流进度数据模型"""
    workflow_id: str  # 工作流ID
    workflow_name: str  # 工作流名称
    
    # 步骤列表
    steps: List[WorkflowStep]
    
    # 进度信息
    current_step_id: Optional[str] = None  # 当前步骤ID
    overall_progress: float = 0.0  # 整体进度(0-100)
    overall_status: StepStatus = StepStatus.PENDING  # 整体状态
    
    # 时间信息
    started_at: Optional[str] = None  # 开始时间
    completed_at: Optional[str] = None  # 完成时间
    estimated_completion: Optional[str] = None  # 预计完成时间
    total_duration_seconds: Optional[float] = None  # 总持续时间(秒)
    
    # 元数据
    created_at: str = None  # 创建时间
    metadata: Optional[Dict] = None  # 元数据


# ==================== 进度跟踪器 ====================

class ProgressTracker:
    """
    进度跟踪器类
    
    提供以下功能:
    - 工作流步骤管理
    - 实时进度跟踪
    - 进度计算
    - 进度回调
    """
    
    # 默认工作流步骤
    DEFAULT_WORKFLOW_STEPS = [
        {
            "id": "collect_info",
            "name": "收集信息",
            "description": "从文件或URL收集员工信息",
            "order": 1
        },
        {
            "id": "analyze_present",
            "name": "分析呈现",
            "description": "结构化展示员工信息,等待确认",
            "order": 2
        },
        {
            "id": "generate_strategy",
            "name": "生成访谈思路",
            "description": "生成个性化访谈思路,等待确认",
            "order": 3
        },
        {
            "id": "generate_outline",
            "name": "生成完整提纲",
            "description": "生成包含开场、核心问题、敏感问题、总结的完整提纲",
            "order": 4
        },
        {
            "id": "output_optimize",
            "name": "输出优化",
            "description": "格式化输出,支持多种格式",
            "order": 5
        }
    ]
    
    def __init__(self, workflow_name: str = "访谈提纲生成"):
        """
        初始化进度跟踪器
        
        Args:
            workflow_name: 工作流名称
        """
        self.workflow_name = workflow_name
        self.workflow_id = self._generate_workflow_id()
        self.progress: Optional[WorkflowProgress] = None
        self.progress_callbacks: List[Callable[[WorkflowProgress], None]] = []
        
        # 初始化工作流
        self._initialize_workflow()
    
    def _generate_workflow_id(self) -> str:
        """
        生成工作流ID
        
        Returns:
            工作流ID
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"workflow_{timestamp}"
    
    def _initialize_workflow(self) -> None:
        """初始化工作流"""
        steps = []
        for step_data in self.DEFAULT_WORKFLOW_STEPS:
            step = WorkflowStep(
                id=step_data["id"],
                name=step_data["name"],
                description=step_data["description"],
                status=StepStatus.PENDING,
                order=step_data["order"]
            )
            steps.append(step)
        
        self.progress = WorkflowProgress(
            workflow_id=self.workflow_id,
            workflow_name=self.workflow_name,
            steps=steps,
            created_at=datetime.now().isoformat()
        )
        
        logger.info(f"初始化工作流: {self.workflow_name} ({self.workflow_id})")
    
    def start_workflow(self) -> None:
        """启动工作流"""
        if self.progress:
            self.progress.started_at = datetime.now().isoformat()
            self.progress.overall_status = StepStatus.IN_PROGRESS
            logger.info(f"启动工作流: {self.workflow_name}")
    
    def complete_workflow(self) -> None:
        """完成工作流"""
        if self.progress:
            self.progress.completed_at = datetime.now().isoformat()
            self.progress.overall_status = StepStatus.COMPLETED
            
            # 计算总持续时间
            if self.progress.started_at:
                start = datetime.fromisoformat(self.progress.started_at)
                end = datetime.fromisoformat(self.progress.completed_at)
                self.progress.total_duration_seconds = (end - start).total_seconds()
            
            logger.info(f"完成工作流: {self.workflow_name} (耗时: {self.progress.total_duration_seconds:.2f}秒)")
    
    def start_step(self, step_id: str) -> None:
        """
        开始步骤
        
        Args:
            step_id: 步骤ID
        """
        if not self.progress:
            return
        
        step = self._get_step_by_id(step_id)
        if step:
            step.status = StepStatus.IN_PROGRESS
            step.started_at = datetime.now().isoformat()
            self.progress.current_step_id = step_id
            
            self._update_overall_progress()
            self._notify_callbacks()
            
            logger.info(f"开始步骤: {step.name}")
    
    def complete_step(self, step_id: str) -> None:
        """
        完成步骤
        
        Args:
            step_id: 步骤ID
        """
        if not self.progress:
            return
        
        step = self._get_step_by_id(step_id)
        if step:
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now().isoformat()
            step.progress_percent = 100.0
            
            # 计算持续时间
            if step.started_at:
                start = datetime.fromisoformat(step.started_at)
                end = datetime.fromisoformat(step.completed_at)
                step.duration_seconds = (end - start).total_seconds()
            
            self._update_overall_progress()
            self._notify_callbacks()
            
            logger.info(f"完成步骤: {step.name} (耗时: {step.duration_seconds:.2f}秒)")
    
    def fail_step(self, step_id: str, error_message: str, error_details: str = None) -> None:
        """
        步骤失败
        
        Args:
            step_id: 步骤ID
            error_message: 错误消息
            error_details: 错误详情
        """
        if not self.progress:
            return
        
        step = self._get_step_by_id(step_id)
        if step:
            step.status = StepStatus.FAILED
            step.error_message = error_message
            step.error_details = error_details
            
            self.progress.overall_status = StepStatus.FAILED
            self._update_overall_progress()
            self._notify_callbacks()
            
            logger.error(f"步骤失败: {step.name} - {error_message}")
    
    def skip_step(self, step_id: str) -> None:
        """
        跳过步骤
        
        Args:
            step_id: 步骤ID
        """
        if not self.progress:
            return
        
        step = self._get_step_by_id(step_id)
        if step:
            step.status = StepStatus.SKIPPED
            step.progress_percent = 100.0
            
            self._update_overall_progress()
            self._notify_callbacks()
            
            logger.info(f"跳过步骤: {step.name}")
    
    def update_step_progress(self, step_id: str, progress_percent: float) -> None:
        """
        更新步骤进度
        
        Args:
            step_id: 步骤ID
            progress_percent: 进度百分比(0-100)
        """
        if not self.progress:
            return
        
        step = self._get_step_by_id(step_id)
        if step:
            step.progress_percent = max(0.0, min(100.0, progress_percent))
            
            self._update_overall_progress()
            self._notify_callbacks()
    
    def add_sub_step(
        self,
        parent_step_id: str,
        sub_step_id: str,
        name: str,
        description: str = ""
    ) -> None:
        """
        添加子步骤
        
        Args:
            parent_step_id: 父步骤ID
            sub_step_id: 子步骤ID
            name: 子步骤名称
            description: 子步骤描述
        """
        if not self.progress:
            return
        
        parent_step = self._get_step_by_id(parent_step_id)
        if parent_step:
            if parent_step.sub_steps is None:
                parent_step.sub_steps = []
            
            sub_step = WorkflowStep(
                id=sub_step_id,
                name=name,
                description=description,
                status=StepStatus.PENDING,
                order=len(parent_step.sub_steps) + 1
            )
            parent_step.sub_steps.append(sub_step)
            
            logger.info(f"添加子步骤: {name} (父步骤: {parent_step.name})")
    
    def get_progress(self) -> Optional[WorkflowProgress]:
        """
        获取当前进度
        
        Returns:
            工作流进度对象
        """
        return self.progress
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """
        获取步骤
        
        Args:
            step_id: 步骤ID
            
        Returns:
            步骤对象,如果不存在则返回None
        """
        return self._get_step_by_id(step_id)
    
    def _get_step_by_id(self, step_id: str) -> Optional[WorkflowStep]:
        """
        根据ID获取步骤
        
        Args:
            step_id: 步骤ID
            
        Returns:
            步骤对象,如果不存在则返回None
        """
        if not self.progress:
            return None
        
        # 查找主步骤
        for step in self.progress.steps:
            if step.id == step_id:
                return step
            
            # 查找子步骤
            if step.sub_steps:
                for sub_step in step.sub_steps:
                    if sub_step.id == step_id:
                        return sub_step
        
        return None
    
    def _update_overall_progress(self) -> None:
        """更新整体进度"""
        if not self.progress:
            return
        
        total_steps = len(self.progress.steps)
        completed_steps = 0
        total_progress = 0.0
        
        for step in self.progress.steps:
            # 统计完成步骤数
            if step.status == StepStatus.COMPLETED:
                completed_steps += 1
                total_progress += 100.0
            elif step.status == StepStatus.SKIPPED:
                completed_steps += 1
                total_progress += 100.0
            elif step.status == StepStatus.FAILED:
                total_progress += step.progress_percent
            else:
                total_progress += step.progress_percent
        
        # 计算整体进度
        self.progress.overall_progress = total_progress / total_steps if total_steps > 0 else 0.0
        
        # 计算预计完成时间
        if self.progress.started_at and self.progress.overall_progress > 0:
            start = datetime.fromisoformat(self.progress.started_at)
            elapsed = (datetime.now() - start).total_seconds()
            if self.progress.overall_progress < 100:
                estimated_total = elapsed * 100 / self.progress.overall_progress
                estimated_completion = start.timestamp() + estimated_total
                self.progress.estimated_completion = datetime.fromtimestamp(estimated_completion).isoformat()
    
    def register_callback(self, callback: Callable[[WorkflowProgress], None]) -> None:
        """
        注册进度回调函数
        
        Args:
            callback: 回调函数
        """
        self.progress_callbacks.append(callback)
        logger.info(f"注册进度回调函数: {callback.__name__}")
    
    def _notify_callbacks(self) -> None:
        """通知所有回调函数"""
        for callback in self.progress_callbacks:
            try:
                callback(self.progress)
            except Exception as e:
                logger.error(f"进度回调失败: {e}")
    
    def get_progress_summary(self) -> str:
        """
        获取进度摘要
        
        Returns:
            进度摘要字符串
        """
        if not self.progress:
            return "无进度信息"
        
        summary = f"""
工作流: {self.progress.workflow_name} ({self.progress.workflow_id})
整体状态: {self.progress.overall_status.value}
整体进度: {self.progress.overall_progress:.1f}%

"""
        
        for step in self.progress.steps:
            status_icon = {
                StepStatus.PENDING: "○",
                StepStatus.IN_PROGRESS: "◐",
                StepStatus.COMPLETED: "●",
                StepStatus.FAILED: "✗",
                StepStatus.SKIPPED: "⊘"
            }.get(step.status, "?")
            
            summary += f"{status_icon} {step.name}: {step.progress_percent:.0f}%"
            
            if step.error_message:
                summary += f" (错误: {step.error_message})"
            
            summary += "\n"
        
        return summary


# ==================== 工厂类 ====================

class ProgressTrackerFactory:
    """进度跟踪器工厂类"""
    
    @staticmethod
    def create_tracker(workflow_name: str = "访谈提纲生成") -> ProgressTracker:
        """
        创建进度跟踪器实例
        
        Args:
            workflow_name: 工作流名称
            
        Returns:
            进度跟踪器实例
        """
        return ProgressTracker(workflow_name=workflow_name)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例1: 创建进度跟踪器
    tracker = ProgressTrackerFactory.create_tracker("示例工作流")
    
    # 示例2: 注册进度回调
    def progress_callback(progress: WorkflowProgress):
        print(f"\r进度: {progress.overall_progress:.1f}%", end="", flush=True)
    
    tracker.register_callback(progress_callback)
    
    # 示例3: 执行工作流
    tracker.start_workflow()
    
    # 步骤1: 收集信息
    tracker.start_step("collect_info")
    # 模拟进度更新
    for i in range(0, 101, 10):
        tracker.update_step_progress("collect_info", float(i))
    tracker.complete_step("collect_info")
    
    # 步骤2: 分析呈现
    tracker.start_step("analyze_present")
    tracker.complete_step("analyze_present")
    
    # 步骤3: 生成访谈思路
    tracker.start_step("generate_strategy")
    tracker.complete_step("generate_strategy")
    
    # 步骤4: 生成完整提纲
    tracker.start_step("generate_outline")
    for i in range(0, 101, 20):
        tracker.update_step_progress("generate_outline", float(i))
    tracker.complete_step("generate_outline")
    
    # 步骤5: 输出优化
    tracker.start_step("output_optimize")
    tracker.complete_step("output_optimize")
    
    tracker.complete_workflow()
    
    # 示例4: 打印进度摘要
    print("\n" + tracker.get_progress_summary())
    
    # 示例5: 获取步骤信息
    step = tracker.get_step("collect_info")
    if step:
        print(f"\n步骤详情:")
        print(f"  名称: {step.name}")
        print(f"  状态: {step.status.value}")
        print(f"  耗时: {step.duration_seconds:.2f}秒")

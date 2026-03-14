"""
错误处理模块

该模块提供统一的错误处理机制,包括错误码体系、友好提示、错误恢复等功能。

作者: tommyyang@tencent
版本: 3.0.0
更新时间: 2026-03-14
"""

import logging
import traceback
from typing import Dict, Optional, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 枚举定义 ====================

class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    LOW = "low"  # 低 - 可继续执行
    MEDIUM = "medium"  # 中 - 需要处理
    HIGH = "high"  # 高 - 需要立即处理
    CRITICAL = "critical"  # 严重 - 系统级错误


class ErrorCategory(Enum):
    """错误类别枚举"""
    VALIDATION = "validation"  # 校验错误
    FILE_PROCESSING = "file_processing"  # 文件处理错误
    TOOL_CALL = "tool_call"  # 工具调用错误
    NETWORK = "network"  # 网络错误
    SYSTEM = "system"  # 系统错误
    USER_INPUT = "user_input"  # 用户输入错误
    PERMISSION = "permission"  # 权限错误


# ==================== 数据模型 ====================

@dataclass
class ErrorDefinition:
    """错误定义数据模型"""
    code: str  # 错误码
    name: str  # 错误名称
    category: ErrorCategory  # 错误类别
    severity: ErrorSeverity  # 严重程度
    message_template: str  # 消息模板
    suggestion: str  # 建议
    retry_allowed: bool = True  # 是否允许重试
    max_retries: int = 3  # 最大重试次数


@dataclass
class ErrorRecord:
    """错误记录数据模型"""
    error_id: str  # 错误ID
    error_code: str  # 错误码
    category: ErrorCategory  # 错误类别
    severity: ErrorSeverity  # 严重程度
    
    # 错误信息
    message: str  # 错误消息
    details: Optional[str] = None  # 错误详情
    suggestion: Optional[str] = None  # 建议
    
    # 上下文信息
    context: Optional[Dict[str, Any]] = None  # 错误上下文
    stack_trace: Optional[str] = None  # 堆栈跟踪
    
    # 时间信息
    occurred_at: str = None  # 发生时间
    
    # 重试信息
    retry_count: int = 0  # 重试次数
    retry_allowed: bool = True  # 是否允许重试
    
    # 处理信息
    handled: bool = False  # 是否已处理
    resolution: Optional[str] = None  # 解决方案
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error_id": self.error_id,
            "error_code": self.error_code,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "suggestion": self.suggestion,
            "context": self.context,
            "occurred_at": self.occurred_at,
            "retry_count": self.retry_count,
            "retry_allowed": self.retry_allowed,
            "handled": self.handled,
            "resolution": self.resolution
        }


# ==================== 错误处理器 ====================

class ErrorHandler:
    """
    错误处理器类
    
    提供以下功能:
    - 统一的错误码体系
    - 友好的错误提示
    - 错误记录和跟踪
    - 错误恢复机制
    """
    
    # 错误定义
    ERROR_DEFINITIONS: Dict[str, ErrorDefinition] = {
        # 强制校验错误
        "HARD_GATE_001": ErrorDefinition(
            code="HARD_GATE_001",
            name="强制校验失败",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
            message_template="缺少核心信息: {missing_fields}",
            suggestion="请提供访谈类型、员工职级和访谈目的",
            retry_allowed=False
        ),
        
        # 文件处理错误
        "FILE_SIZE_001": ErrorDefinition(
            code="FILE_SIZE_001",
            name="文件大小超限",
            category=ErrorCategory.FILE_PROCESSING,
            severity=ErrorSeverity.MEDIUM,
            message_template="文件大小超限: {file_size}MB > {limit}MB",
            suggestion="请压缩文件或减少文件大小",
            retry_allowed=False
        ),
        
        "FILE_TYPE_001": ErrorDefinition(
            code="FILE_TYPE_001",
            name="不支持的文件类型",
            category=ErrorCategory.FILE_PROCESSING,
            severity=ErrorSeverity.MEDIUM,
            message_template="不支持的文件类型: {file_type}",
            suggestion="支持的格式: Excel(.xlsx, .xls), PDF(.pdf), Word(.docx, .doc), PPTX(.pptx), TXT(.txt)",
            retry_allowed=False
        ),
        
        "FILE_PARSE_001": ErrorDefinition(
            code="FILE_PARSE_001",
            name="文件解析失败",
            category=ErrorCategory.FILE_PROCESSING,
            severity=ErrorSeverity.HIGH,
            message_template="无法解析文件: {file_path}",
            suggestion="请检查文件是否损坏或格式是否正确",
            retry_allowed=True,
            max_retries=2
        ),
        
        "FILE_ACCESS_001": ErrorDefinition(
            code="FILE_ACCESS_001",
            name="文件访问失败",
            category=ErrorCategory.FILE_PROCESSING,
            severity=ErrorSeverity.HIGH,
            message_template="无法访问文件: {file_path}",
            suggestion="请检查文件路径和访问权限",
            retry_allowed=True,
            max_retries=2
        ),
        
        # URL访问错误
        "URL_FETCH_001": ErrorDefinition(
            code="URL_FETCH_001",
            name="URL访问失败",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message_template="无法访问URL: {url}",
            suggestion="请检查URL是否正确,是否有访问权限",
            retry_allowed=True,
            max_retries=3
        ),
        
        # 工具调用错误
        "TOOL_CALL_001": ErrorDefinition(
            code="TOOL_CALL_001",
            name="工具调用失败",
            category=ErrorCategory.TOOL_CALL,
            severity=ErrorSeverity.HIGH,
            message_template="工具调用失败: {tool_name}",
            suggestion="请稍后重试或联系技术支持",
            retry_allowed=True,
            max_retries=3
        ),
        
        # 系统错误
        "SYSTEM_001": ErrorDefinition(
            code="SYSTEM_001",
            name="系统错误",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            message_template="系统发生错误: {error_details}",
            suggestion="请联系技术支持",
            retry_allowed=True,
            max_retries=1
        ),
        
        # 用户输入错误
        "USER_INPUT_001": ErrorDefinition(
            code="USER_INPUT_001",
            name="用户输入错误",
            category=ErrorCategory.USER_INPUT,
            severity=ErrorSeverity.LOW,
            message_template="无效的用户输入: {input_value}",
            suggestion="请检查输入内容",
            retry_allowed=False
        ),
        
        # 权限错误
        "PERMISSION_001": ErrorDefinition(
            code="PERMISSION_001",
            name="权限不足",
            category=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.HIGH,
            message_template="权限不足: {operation}",
            suggestion="请联系管理员获取相应权限",
            retry_allowed=False
        )
    }
    
    def __init__(self):
        """初始化错误处理器"""
        self.error_records: List[ErrorRecord] = []
        self.error_handlers: Dict[str, Callable[[ErrorRecord], bool]] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_error_definition(self, error_code: str) -> Optional[ErrorDefinition]:
        """
        获取错误定义
        
        Args:
            error_code: 错误码
            
        Returns:
            错误定义,如果不存在则返回None
        """
        return self.ERROR_DEFINITIONS.get(error_code)
    
    def create_error_record(
        self,
        error_code: str,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None
    ) -> ErrorRecord:
        """
        创建错误记录
        
        Args:
            error_code: 错误码
            context: 错误上下文
            stack_trace: 堆栈跟踪
            
        Returns:
            错误记录
        """
        error_def = self.get_error_definition(error_code)
        
        if not error_def:
            # 如果错误码不存在,创建一个默认错误
            error_def = ErrorDefinition(
                code=error_code,
                name="未知错误",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                message_template="未知错误: {error_code}",
                suggestion="请联系技术支持",
                retry_allowed=True
            )
        
        # 格式化消息
        message = self._format_message(error_def.message_template, context or {})
        
        # 创建错误记录
        error_id = self._generate_error_id(error_code)
        error_record = ErrorRecord(
            error_id=error_id,
            error_code=error_code,
            category=error_def.category,
            severity=error_def.severity,
            message=message,
            details=error_def.suggestion,
            suggestion=error_def.suggestion,
            context=context,
            stack_trace=stack_trace,
            occurred_at=datetime.now().isoformat(),
            retry_allowed=error_def.retry_allowed
        )
        
        return error_record
    
    def _format_message(self, template: str, context: Dict[str, Any]) -> str:
        """
        格式化消息模板
        
        Args:
            template: 消息模板
            context: 上下文
            
        Returns:
            格式化后的消息
        """
        try:
            return template.format(**context)
        except KeyError as e:
            self.logger.warning(f"消息格式化失败,缺少键: {e}")
            return template
        except Exception as e:
            self.logger.error(f"消息格式化失败: {e}")
            return template
    
    def _generate_error_id(self, error_code: str) -> str:
        """
        生成错误ID
        
        Args:
            error_code: 错误码
            
        Returns:
            错误ID
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import hashlib
        hash_obj = hashlib.md5(f"{error_code}{timestamp}".encode())
        return f"{error_code}_{hash_obj.hexdigest()[:8]}"
    
    def handle_error(
        self,
        error_code: str,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> ErrorRecord:
        """
        处理错误
        
        Args:
            error_code: 错误码
            context: 错误上下文
            exception: 异常对象
            
        Returns:
            错误记录
        """
        # 获取堆栈跟踪
        stack_trace = None
        if exception:
            stack_trace = traceback.format_exc()
        
        # 创建错误记录
        error_record = self.create_error_record(error_code, context, stack_trace)
        
        # 记录错误
        self.error_records.append(error_record)
        
        # 记录日志
        self._log_error(error_record)
        
        # 调用错误处理器
        self._call_error_handlers(error_record)
        
        return error_record
    
    def _log_error(self, error_record: ErrorRecord) -> None:
        """
        记录错误日志
        
        Args:
            error_record: 错误记录
        """
        # 根据严重程度选择日志级别
        log_methods = {
            ErrorSeverity.LOW: self.logger.info,
            ErrorSeverity.MEDIUM: self.logger.warning,
            ErrorSeverity.HIGH: self.logger.error,
            ErrorSeverity.CRITICAL: self.logger.critical
        }
        
        log_method = log_methods.get(error_record.severity, self.logger.error)
        
        # 记录错误
        log_method(
            f"[{error_record.error_code}] {error_record.message}\n"
            f"建议: {error_record.suggestion}"
        )
        
        # 记录堆栈跟踪
        if error_record.stack_trace:
            self.logger.debug(f"堆栈跟踪:\n{error_record.stack_trace}")
    
    def _call_error_handlers(self, error_record: ErrorRecord) -> bool:
        """
        调用错误处理器
        
        Args:
            error_record: 错误记录
            
        Returns:
            是否处理成功
        """
        # 查找注册的处理器
        handler = self.error_handlers.get(error_record.error_code)
        if not handler:
            handler = self.error_handlers.get("*")  # 默认处理器
        
        if handler:
            try:
                result = handler(error_record)
                error_record.handled = True
                error_record.resolution = "已由错误处理器处理"
                return result
            except Exception as e:
                self.logger.error(f"错误处理器执行失败: {e}")
                return False
        
        return False
    
    def register_error_handler(
        self,
        error_code: str,
        handler: Callable[[ErrorRecord], bool]
    ) -> None:
        """
        注册错误处理器
        
        Args:
            error_code: 错误码,使用"*"表示默认处理器
            handler: 错误处理函数
        """
        self.error_handlers[error_code] = handler
        self.logger.info(f"注册错误处理器: {error_code}")
    
    def get_error_records(
        self,
        error_code: Optional[str] = None,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
        handled: Optional[bool] = None
    ) -> List[ErrorRecord]:
        """
        获取错误记录
        
        Args:
            error_code: 错误码(可选)
            category: 错误类别(可选)
            severity: 严重程度(可选)
            handled: 是否已处理(可选)
            
        Returns:
            错误记录列表
        """
        records = self.error_records
        
        # 过滤
        if error_code:
            records = [r for r in records if r.error_code == error_code]
        
        if category:
            records = [r for r in records if r.category == category]
        
        if severity:
            records = [r for r in records if r.severity == severity]
        
        if handled is not None:
            records = [r for r in records if r.handled == handled]
        
        return records
    
    def clear_error_records(self) -> None:
        """清空错误记录"""
        self.error_records.clear()
        self.logger.info("清空错误记录")
    
    def get_error_summary(self) -> str:
        """
        获取错误摘要
        
        Returns:
            错误摘要字符串
        """
        if not self.error_records:
            return "无错误记录"
        
        total = len(self.error_records)
        handled = sum(1 for r in self.error_records if r.handled)
        unhandled = total - handled
        
        # 按严重程度统计
        severity_counts = {}
        for record in self.error_records:
            severity = record.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        summary = f"""
错误摘要:
  总计: {total}
  已处理: {handled}
  未处理: {unhandled}

严重程度分布:
"""
        for severity, count in severity_counts.items():
            summary += f"  {severity}: {count}\n"
        
        return summary


# ==================== 工厂类 ====================

class ErrorHandlerFactory:
    """错误处理器工厂类"""
    
    @staticmethod
    def create_handler() -> ErrorHandler:
        """
        创建错误处理器实例
        
        Returns:
            错误处理器实例
        """
        return ErrorHandler()


# ==================== 装饰器 ====================

def handle_errors(error_handler: ErrorHandler):
    """
    错误处理装饰器
    
    Args:
        error_handler: 错误处理器实例
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 根据异常类型确定错误码
                error_code = "SYSTEM_001"
                error_name = type(e).__name__
                
                # 尝试从异常中提取错误码
                if hasattr(e, 'code'):
                    error_code = e.code
                
                # 处理错误
                context = {
                    "function": func.__name__,
                    "error_type": error_name,
                    "error_message": str(e)
                }
                
                error_record = error_handler.handle_error(
                    error_code=error_code,
                    context=context,
                    exception=e
                )
                
                # 重新抛出异常
                raise
        
        return wrapper
    return decorator


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例1: 创建错误处理器
    handler = ErrorHandlerFactory.create_handler()
    
    # 示例2: 注册错误处理器
    def hard_gate_handler(error_record: ErrorRecord) -> bool:
        print(f"\n处理强制校验失败:")
        print(f"  消息: {error_record.message}")
        print(f"  建议: {error_record.suggestion}")
        return True
    
    handler.register_error_handler("HARD_GATE_001", hard_gate_handler)
    
    # 示例3: 处理错误
    context = {
        "missing_fields": "访谈类型, 员工职级"
    }
    error_record = handler.handle_error("HARD_GATE_001", context)
    
    # 示例4: 获取错误记录
    records = handler.get_error_records(error_code="HARD_GATE_001")
    print(f"\n错误记录数: {len(records)}")
    
    # 示例5: 获取错误摘要
    print(handler.get_error_summary())
    
    # 示例6: 使用装饰器
    @handle_errors(handler)
    def risky_function():
        """可能抛出异常的函数"""
        raise ValueError("测试错误")
    
    # 注释掉避免抛出异常
    # risky_function()

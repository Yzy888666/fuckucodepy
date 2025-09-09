"""
指标系统接口定义

定义代码质量指标的抽象接口和基础实现。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..common.constants import LanguageType
from ..parsers.models import ParseResult
from .models import MetricResult


class Metric(ABC):
    """
    代码质量指标抽象接口
    
    所有质量指标都应该实现这个接口。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        返回指标名称
        
        Returns:
            str: 指标名称
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        返回指标描述
        
        Returns:
            str: 指标描述
        """
        pass
    
    @property
    @abstractmethod
    def weight(self) -> float:
        """
        返回指标权重
        
        Returns:
            float: 权重值 (0.0-1.0)
        """
        pass
    
    @abstractmethod
    def analyze(self, parse_result: ParseResult) -> MetricResult:
        """
        分析代码并计算指标
        
        Args:
            parse_result: 解析结果
            
        Returns:
            MetricResult: 指标结果
        """
        pass
    
    @abstractmethod
    def supported_languages(self) -> List[LanguageType]:
        """
        返回支持的语言类型列表
        
        Returns:
            List[LanguageType]: 支持的语言类型
        """
        pass
    
    def can_analyze(self, language: LanguageType) -> bool:
        """
        检查是否支持指定语言
        
        Args:
            language: 语言类型
            
        Returns:
            bool: 是否支持
        """
        return language in self.supported_languages()
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        获取指标配置
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "supported_languages": [lang.value for lang in self.supported_languages()],
        }


class BaseMetric(Metric):
    """
    基础指标实现
    
    提供所有指标的通用功能。
    """
    
    def __init__(self, name: str, description: str, weight: float = 1.0):
        self._name = name
        self._description = description
        self._weight = weight
        
        # 可配置的阈值
        self._thresholds = self._get_default_thresholds()
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def weight(self) -> float:
        return self._weight
    
    def set_weight(self, weight: float) -> None:
        """
        设置指标权重
        
        Args:
            weight: 权重值 (0.0-1.0)
        """
        self._weight = max(0.0, min(1.0, weight))
    
    def set_threshold(self, key: str, value: Any) -> None:
        """
        设置阈值
        
        Args:
            key: 阈值键名
            value: 阈值
        """
        self._thresholds[key] = value
    
    def get_threshold(self, key: str, default: Any = None) -> Any:
        """
        获取阈值
        
        Args:
            key: 阈值键名
            default: 默认值
            
        Returns:
            Any: 阈值
        """
        return self._thresholds.get(key, default)
    
    def _get_default_thresholds(self) -> Dict[str, Any]:
        """
        获取默认阈值配置
        
        Returns:
            Dict[str, Any]: 默认阈值
        """
        return {}
    
    def _normalize_score(self, raw_score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """
        规范化分数到0-1范围
        
        Args:
            raw_score: 原始分数
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            float: 规范化后的分数
        """
        if max_val <= min_val:
            return 0.0
        
        normalized = (raw_score - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    def _create_metric_result(self, score: float, issues: List = None, 
                            details: Dict[str, Any] = None, 
                            raw_data: Dict[str, Any] = None) -> MetricResult:
        """
        创建指标结果对象
        
        Args:
            score: 评分
            issues: 问题列表
            details: 详细信息
            raw_data: 原始数据
            
        Returns:
            MetricResult: 指标结果
        """
        from .models import MetricResult
        
        return MetricResult(
            metric_name=self.name,
            score=score,
            weight=self.weight,
            description=self.description,
            issues=issues or [],
            details=details or {},
            raw_data=raw_data or {}
        )
    
    def _calculate_score_by_threshold(self, value: float, thresholds: Dict[str, float]) -> float:
        """
        根据阈值计算分数
        
        Args:
            value: 待评估的值
            thresholds: 阈值配置 {"excellent": x, "good": y, "poor": z}
            
        Returns:
            float: 计算得出的分数 (0.0-1.0)
        """
        excellent = thresholds.get("excellent", 0)
        good = thresholds.get("good", excellent * 2)
        poor = thresholds.get("poor", good * 2)
        
        if value <= excellent:
            return 0.0  # 优秀
        elif value <= good:
            # 线性插值 excellent -> good 对应 0.0 -> 0.3
            return 0.3 * (value - excellent) / (good - excellent)
        elif value <= poor:
            # 线性插值 good -> poor 对应 0.3 -> 0.7
            return 0.3 + 0.4 * (value - good) / (poor - good)
        else:
            # 超过poor阈值，分数为 0.7 + 额外惩罚
            excess_factor = (value - poor) / poor if poor > 0 else 1
            return min(1.0, 0.7 + 0.3 * excess_factor)
    
    def supported_languages(self) -> List[LanguageType]:
        """
        默认支持所有语言
        子类可以重写这个方法来限制支持的语言
        """
        return [
            LanguageType.PYTHON,
            LanguageType.JAVASCRIPT,
            LanguageType.TYPESCRIPT,
            LanguageType.JAVA,
            LanguageType.C,
            LanguageType.CPP,
        ]
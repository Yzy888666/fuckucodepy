"""
指标工厂

管理所有指标的创建、配置和组织。
"""

from typing import Dict, List, Optional, Type
from ..common.constants import LanguageType, DEFAULT_METRIC_WEIGHTS
from ..common.exceptions import MetricError
from .interfaces import Metric
from .complexity import ComplexityMetric
from .function_length import FunctionLengthMetric
from .comment_ratio import CommentRatioMetric


class MetricFactory:
    """
    指标工厂类
    
    管理所有质量指标的创建和配置。
    """
    
    def __init__(self):
        self._metrics: Dict[str, Type[Metric]] = {}
        self._instances: Dict[str, Metric] = {}
        self._weights: Dict[str, float] = DEFAULT_METRIC_WEIGHTS.copy()
        
        # 注册内置指标
        self._register_builtin_metrics()
    
    def _register_builtin_metrics(self) -> None:
        """注册内置指标"""
        self.register_metric("complexity", ComplexityMetric)
        self.register_metric("function_length", FunctionLengthMetric)
        self.register_metric("comment_ratio", CommentRatioMetric)
        
        # TODO: 注册其他指标
        # self.register_metric("error_handling", ErrorHandlingMetric)
        # self.register_metric("naming_convention", NamingConventionMetric)
        # self.register_metric("code_duplication", CodeDuplicationMetric)
        # self.register_metric("structure_analysis", StructureAnalysisMetric)
    
    def register_metric(self, name: str, metric_class: Type[Metric]) -> None:
        """
        注册指标
        
        Args:
            name: 指标名称（用作标识符）
            metric_class: 指标类
        """
        self._metrics[name] = metric_class
    
    def create_metric(self, name: str) -> Metric:
        """
        创建指标实例
        
        Args:
            name: 指标名称
            
        Returns:
            Metric: 指标实例
            
        Raises:
            MetricError: 指标不存在
        """
        if name not in self._metrics:
            raise MetricError(f"未知指标: {name}", name)
        
        # 使用单例模式，避免重复创建
        if name not in self._instances:
            metric_class = self._metrics[name]
            metric = metric_class()
            
            # 设置自定义权重
            if name in self._weights:
                metric.set_weight(self._weights[name])
            
            self._instances[name] = metric
        
        return self._instances[name]
    
    def create_all_metrics(self) -> List[Metric]:
        """
        创建所有已注册的指标
        
        Returns:
            List[Metric]: 指标列表
        """
        return [self.create_metric(name) for name in self._metrics.keys()]
    
    def create_metrics_for_language(self, language: LanguageType) -> List[Metric]:
        """
        创建支持指定语言的指标
        
        Args:
            language: 语言类型
            
        Returns:
            List[Metric]: 支持该语言的指标列表
        """
        metrics = []
        for name in self._metrics.keys():
            metric = self.create_metric(name)
            if metric.can_analyze(language):
                metrics.append(metric)
        
        return metrics
    
    def get_metric_names(self) -> List[str]:
        """
        获取所有已注册指标的名称
        
        Returns:
            List[str]: 指标名称列表
        """
        return list(self._metrics.keys())
    
    def is_metric_registered(self, name: str) -> bool:
        """
        检查指标是否已注册
        
        Args:
            name: 指标名称
            
        Returns:
            bool: 是否已注册
        """
        return name in self._metrics
    
    def set_metric_weight(self, name: str, weight: float) -> None:
        """
        设置指标权重
        
        Args:
            name: 指标名称
            weight: 权重值 (0.0-1.0)
            
        Raises:
            MetricError: 指标不存在
        """
        if name not in self._metrics:
            raise MetricError(f"未知指标: {name}", name)
        
        weight = max(0.0, min(1.0, weight))
        self._weights[name] = weight
        
        # 如果实例已存在，更新其权重
        if name in self._instances:
            self._instances[name].set_weight(weight)
    
    def get_metric_weight(self, name: str) -> Optional[float]:
        """
        获取指标权重
        
        Args:
            name: 指标名称
            
        Returns:
            Optional[float]: 权重值，如果指标不存在则返回None
        """
        return self._weights.get(name)
    
    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        批量设置指标权重
        
        Args:
            weights: 权重配置字典
        """
        for name, weight in weights.items():
            if name in self._metrics:
                self.set_metric_weight(name, weight)
    
    def get_weights(self) -> Dict[str, float]:
        """
        获取所有指标权重
        
        Returns:
            Dict[str, float]: 权重配置字典
        """
        return self._weights.copy()
    
    def normalize_weights(self) -> None:
        """
        归一化权重，使总和为1.0
        """
        total_weight = sum(self._weights.values())
        if total_weight > 0:
            for name in self._weights:
                self._weights[name] /= total_weight
                # 更新实例权重
                if name in self._instances:
                    self._instances[name].set_weight(self._weights[name])
    
    def get_metric_info(self, name: str) -> Optional[Dict[str, any]]:
        """
        获取指标信息
        
        Args:
            name: 指标名称
            
        Returns:
            Optional[Dict[str, any]]: 指标信息，如果不存在则返回None
        """
        if name not in self._metrics:
            return None
        
        metric = self.create_metric(name)
        return {
            "name": metric.name,
            "description": metric.description,
            "weight": metric.weight,
            "supported_languages": [lang.value for lang in metric.supported_languages()],
            "identifier": name,
        }
    
    def get_all_metrics_info(self) -> List[Dict[str, any]]:
        """
        获取所有指标信息
        
        Returns:
            List[Dict[str, any]]: 指标信息列表
        """
        return [self.get_metric_info(name) for name in self._metrics.keys()]
    
    def clear_cache(self) -> None:
        """清理指标实例缓存"""
        self._instances.clear()
    
    def reset_weights(self) -> None:
        """重置权重为默认值"""
        self._weights = DEFAULT_METRIC_WEIGHTS.copy()
        # 更新已创建的实例
        for name, metric in self._instances.items():
            if name in self._weights:
                metric.set_weight(self._weights[name])


# 全局工厂实例
_metric_factory = MetricFactory()


def get_metric_factory() -> MetricFactory:
    """
    获取全局指标工厂实例
    
    Returns:
        MetricFactory: 工厂实例
    """
    return _metric_factory


def create_metric(name: str) -> Metric:
    """
    创建指标的便捷函数
    
    Args:
        name: 指标名称
        
    Returns:
        Metric: 指标实例
    """
    return _metric_factory.create_metric(name)


def create_all_metrics() -> List[Metric]:
    """
    创建所有指标的便捷函数
    
    Returns:
        List[Metric]: 指标列表
    """
    return _metric_factory.create_all_metrics()


def create_metrics_for_language(language: LanguageType) -> List[Metric]:
    """
    为语言创建指标的便捷函数
    
    Args:
        language: 语言类型
        
    Returns:
        List[Metric]: 支持该语言的指标列表
    """
    return _metric_factory.create_metrics_for_language(language)
"""
代码分析器

主要的代码分析实现，集成解析器和指标系统。
"""

import os
import time
from datetime import datetime
from typing import List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..common.constants import QUALITY_THRESHOLDS, QualityLevel
from ..common.file_utils import FileUtils
from ..common.language_detector import LanguageDetector
from ..common.exceptions import (
    AnalysisError, 
    FileNotFoundError, 
    UnsupportedLanguageError,
    PermissionError as FuckUCodePermissionError
)
from ..parsers.factory import get_parser_factory
from ..metrics.factory import get_metric_factory
from ..metrics.models import MetricSummary
from .interfaces import Analyzer
from .models import AnalysisResult, AnalysisConfig, FileAnalysisResult


class CodeAnalyzer(Analyzer):
    """
    代码分析器
    
    集成解析器和指标系统，提供完整的代码质量分析功能。
    """
    
    def __init__(self):
        self._file_utils = FileUtils()
        self._language_detector = LanguageDetector()
        self._parser_factory = get_parser_factory()
        self._metric_factory = get_metric_factory()
        
        # 默认配置
        self._default_config = AnalysisConfig(target_path="")
    
    @property
    def name(self) -> str:
        return "CodeAnalyzer"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def analyze(
        self, 
        path: str, 
        config: Optional[AnalysisConfig] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> AnalysisResult:
        """
        分析指定路径的代码
        
        Args:
            path: 文件或目录路径
            config: 分析配置
            progress_callback: 进度回调函数
            
        Returns:
            AnalysisResult: 分析结果
        """
        # 使用提供的配置或默认配置
        if config is None:
            config = AnalysisConfig(target_path=path)
        else:
            config.target_path = path
        
        # 创建分析结果对象
        result = AnalysisResult(
            target_path=path,
            start_time=datetime.now(),
            config=config
        )
        
        try:
            # 验证路径
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            
            # 设置自定义权重
            if config.custom_weights:
                self._metric_factory.set_weights(config.custom_weights)
            
            # 查找源代码文件
            if progress_callback:
                progress_callback("正在搜索源代码文件...", 0.0)
            
            files = self._find_source_files(path, config)
            
            if not files:
                result.add_error("没有找到可分析的源代码文件")
                result.end_time = datetime.now()
                return result
            
            # 限制文件数量
            if config.max_files and len(files) > config.max_files:
                files = files[:config.max_files]
                result.add_error(f"文件数量超过限制，仅分析前{config.max_files}个文件")
            
            # 分析文件
            self._analyze_files(files, result, config, progress_callback)
            
            # 计算总体评分和等级
            self._calculate_overall_results(result)
            
        except Exception as e:
            result.add_error(f"分析过程发生错误: {str(e)}")
        
        finally:
            result.end_time = datetime.now()
            result.calculate_statistics()
        
        return result
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            AnalysisResult: 分析结果
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(file_path)
        
        return self.analyze(file_path)
    
    def _find_source_files(self, path: str, config: AnalysisConfig) -> List[str]:
        """
        查找源代码文件
        
        Args:
            path: 路径
            config: 配置
            
        Returns:
            List[str]: 文件路径列表
        """
        try:
            files = list(self._file_utils.find_source_files(
                root_path=path,
                include_patterns=config.include_patterns if config.include_patterns else None,
                exclude_patterns=config.exclude_patterns if config.exclude_patterns else None
            ))
            
            # 过滤支持的语言
            if config.languages:
                supported_files = []
                for file_path in files:
                    try:
                        language = self._language_detector.detect_language(file_path)
                        if language in config.languages:
                            supported_files.append(file_path)
                    except UnsupportedLanguageError:
                        continue
                files = supported_files
            else:
                # 只保留支持的文件
                files = [f for f in files if self._parser_factory.is_supported_file(f)]
            
            return files
            
        except FuckUCodePermissionError as e:
            raise AnalysisError(f"权限不足: {e}")
        except Exception as e:
            raise AnalysisError(f"搜索文件失败: {e}")
    
    def _analyze_files(
        self,
        files: List[str],
        result: AnalysisResult,
        config: AnalysisConfig,
        progress_callback: Optional[Callable[[str, float], None]]
    ) -> None:
        """
        分析文件列表
        
        Args:
            files: 文件路径列表
            result: 分析结果对象
            config: 配置
            progress_callback: 进度回调
        """
        total_files = len(files)
        completed_files = 0
        
        if config.parallel and total_files > 1:
            # 并行分析
            max_workers = min(4, os.cpu_count() or 1)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_file = {
                    executor.submit(self._analyze_single_file, file_path, config): file_path
                    for file_path in files
                }
                
                # 收集结果
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    completed_files += 1
                    
                    try:
                        file_result = future.result(timeout=config.timeout)
                        result.add_file_result(file_result)
                    except Exception as e:
                        # 创建错误结果
                        error_result = FileAnalysisResult(
                            file_path=file_path,
                            language=self._language_detector.detect_language(file_path)
                        )
                        error_result.add_error(f"分析失败: {str(e)}")
                        result.add_file_result(error_result)
                    
                    # 更新进度
                    if progress_callback:
                        progress = completed_files / total_files
                        relative_path = os.path.relpath(file_path, result.target_path)
                        progress_callback(f"正在分析: {relative_path}", progress)
        else:
            # 串行分析
            for i, file_path in enumerate(files):
                try:
                    file_result = self._analyze_single_file(file_path, config)
                    result.add_file_result(file_result)
                except Exception as e:
                    # 创建错误结果
                    error_result = FileAnalysisResult(
                        file_path=file_path,
                        language=self._language_detector.detect_language(file_path)
                    )
                    error_result.add_error(f"分析失败: {str(e)}")
                    result.add_file_result(error_result)
                
                # 更新进度
                if progress_callback:
                    progress = (i + 1) / total_files
                    relative_path = os.path.relpath(file_path, result.target_path)
                    progress_callback(f"正在分析: {relative_path}", progress)
    
    def _analyze_single_file(self, file_path: str, config: AnalysisConfig) -> FileAnalysisResult:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            config: 配置
            
        Returns:
            FileAnalysisResult: 文件分析结果
        """
        start_time = time.time()
        
        # 检测语言
        language = self._language_detector.detect_language(file_path)
        
        # 创建结果对象
        file_result = FileAnalysisResult(
            file_path=file_path,
            language=language
        )
        
        try:
            # 解析代码
            parser = self._parser_factory.create_parser_for_file(file_path)
            content = self._file_utils.read_file_content(file_path)
            parse_result = parser.parse(file_path, content)
            file_result.parse_result = parse_result
            
            # 应用指标
            metrics = self._metric_factory.create_metrics_for_language(language)
            
            # 如果指定了特定指标，只使用指定的指标
            if config.metrics:
                metrics = [m for m in metrics if any(name in m.name for name in config.metrics)]
            
            for metric in metrics:
                try:
                    metric_result = metric.analyze(parse_result)
                    file_result.metric_results.append(metric_result)
                except Exception as e:
                    file_result.add_error(f"指标 '{metric.name}' 计算失败: {str(e)}")
            
            # 计算质量评分
            file_result.quality_score = self._calculate_file_score(file_result.metric_results)
            file_result.quality_level = self._determine_quality_level(file_result.quality_score)
            
        except UnsupportedLanguageError as e:
            file_result.add_error(f"不支持的语言: {e}")
        except Exception as e:
            file_result.add_error(f"分析文件失败: {str(e)}")
        
        file_result.analysis_time = time.time() - start_time
        return file_result
    
    def _calculate_file_score(self, metric_results: List) -> float:
        """
        计算文件质量评分
        
        Args:
            metric_results: 指标结果列表
            
        Returns:
            float: 质量评分 (0-100)
        """
        if not metric_results:
            return 0.0
        
        # 创建指标汇总
        summary = MetricSummary.from_results(metric_results)
        
        # 将0-1范围的分数转换为0-100范围
        return round(summary.weighted_score * 100, 1)
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """
        根据评分确定质量等级
        
        Args:
            score: 质量评分 (0-100)
            
        Returns:
            QualityLevel: 质量等级
        """
        for min_score, max_score, level in QUALITY_THRESHOLDS:
            if min_score <= score < max_score:
                return level
        
        return QualityLevel.ULTIMATE  # 默认最差等级
    
    def _calculate_overall_results(self, result: AnalysisResult) -> None:
        """
        计算总体分析结果
        
        Args:
            result: 分析结果对象
        """
        if not result.file_results:
            return
        
        # 只考虑成功分析的文件
        successful_files = [f for f in result.file_results if not f.has_errors and f.metric_results]
        
        if not successful_files:
            result.overall_score = 0.0
            result.overall_level = QualityLevel.EXCELLENT
            return
        
        # 计算加权平均分
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for file_result in successful_files:
            # 文件大小作为权重因子（可选）
            file_weight = 1.0
            if file_result.parse_result:
                # 根据代码行数调整权重
                lines = file_result.parse_result.code_lines
                if lines > 0:
                    file_weight = min(3.0, max(0.5, lines / 100))  # 100行为基准权重1.0
            
            total_weighted_score += file_result.quality_score * file_weight
            total_weight += file_weight
        
        # 计算总体评分
        result.overall_score = round(total_weighted_score / total_weight, 1) if total_weight > 0 else 0.0
        result.overall_level = self._determine_quality_level(result.overall_score)
        
        # 创建指标汇总
        all_metric_results = []
        for file_result in successful_files:
            all_metric_results.extend(file_result.metric_results)
        
        if all_metric_results:
            result.metric_summary = MetricSummary.from_results(all_metric_results)
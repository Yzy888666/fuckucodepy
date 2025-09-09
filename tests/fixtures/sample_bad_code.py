"""
测试用的示例Python代码

这个文件故意包含一些代码质量问题，用于测试分析功能。
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional


def bad_function_with_high_complexity(data, flag1, flag2, flag3, mode, options, config, debug):
    """这是一个复杂度很高的函数"""
    result = []
    
    if flag1:
        if flag2:
            if flag3:
                for item in data:
                    if item.get('status') == 'active':
                        if mode == 'fast':
                            if options.get('parallel'):
                                for sub_item in item.get('children', []):
                                    if sub_item.get('enabled'):
                                        try:
                                            processed = process_item(sub_item, config)
                                            if processed:
                                                result.append(processed)
                                        except Exception as e:
                                            if debug:
                                                print(f"Error: {e}")
                                            continue
                            else:
                                for sub_item in item.get('children', []):
                                    if sub_item.get('enabled'):
                                        processed = process_item(sub_item, config)
                                        if processed:
                                            result.append(processed)
                        elif mode == 'slow':
                            # 处理慢模式
                            time.sleep(0.1)
                            result.append(item)
                        else:
                            result.append(item)
                    elif item.get('status') == 'pending':
                        if mode == 'fast':
                            result.append({'id': item.get('id'), 'status': 'skipped'})
                    else:
                        pass
            else:
                for item in data:
                    result.append(item)
        else:
            return []
    
    return result


def process_item(item, config):
    return item


class VeryLongClassWithManyMethods:
    def __init__(self, param1, param2, param3, param4, param5, param6, param7, param8, param9):
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.param4 = param4
        self.param5 = param5
        self.param6 = param6
        self.param7 = param7
        self.param8 = param8
        self.param9 = param9
        self.data = {}
        self.cache = {}
        self.config = {}
        
    def method_without_docstring(self):
        # 这个方法没有文档字符串
        pass
    
    def another_method_without_docstring(self):
        # 这个方法也没有文档字符串
        if self.param1:
            if self.param2:
                return self.param3
            else:
                return self.param4
        return None
    
    def very_long_method_that_does_too_many_things(self, input_data, process_flags, output_options, error_handling_mode, logging_config, performance_settings, validation_rules, transformation_rules, filter_criteria, sort_options):
        # 这是一个超长的方法，做了太多事情
        results = []
        errors = []
        warnings = []
        processed_count = 0
        error_count = 0
        warning_count = 0
        
        # 数据验证阶段
        if validation_rules:
            for rule in validation_rules:
                if rule.get('enabled'):
                    for item in input_data:
                        if not self._validate_item(item, rule):
                            if error_handling_mode == 'strict':
                                raise ValueError(f"Validation failed for item {item}")
                            elif error_handling_mode == 'log':
                                errors.append(f"Validation failed for item {item}")
                                error_count += 1
                            else:
                                warnings.append(f"Validation warning for item {item}")
                                warning_count += 1
        
        # 数据转换阶段
        if transformation_rules:
            for rule in transformation_rules:
                if rule.get('enabled'):
                    try:
                        input_data = self._apply_transformation(input_data, rule)
                    except Exception as e:
                        if error_handling_mode == 'strict':
                            raise
                        else:
                            errors.append(f"Transformation failed: {e}")
                            error_count += 1
        
        # 数据过滤阶段
        if filter_criteria:
            filtered_data = []
            for item in input_data:
                should_include = True
                for criteria in filter_criteria:
                    if not self._check_criteria(item, criteria):
                        should_include = False
                        break
                if should_include:
                    filtered_data.append(item)
            input_data = filtered_data
        
        # 数据处理主循环
        for index, item in enumerate(input_data):
            try:
                if process_flags.get('validate_each_item'):
                    if not self._validate_single_item(item):
                        if error_handling_mode == 'strict':
                            raise ValueError(f"Item validation failed at index {index}")
                        else:
                            error_count += 1
                            continue
                
                processed_item = self._process_single_item(item, performance_settings)
                
                if processed_item:
                    results.append(processed_item)
                    processed_count += 1
                    
                    if logging_config.get('log_each_item'):
                        self._log_item_processing(item, processed_item, index)
                
            except Exception as e:
                error_count += 1
                if error_handling_mode == 'strict':
                    raise
                else:
                    errors.append(f"Processing failed for item {index}: {e}")
        
        # 结果排序
        if sort_options:
            try:
                results = self._sort_results(results, sort_options)
            except Exception as e:
                warnings.append(f"Sorting failed: {e}")
                warning_count += 1
        
        # 输出格式化
        if output_options:
            try:
                results = self._format_output(results, output_options)
            except Exception as e:
                warnings.append(f"Output formatting failed: {e}")
                warning_count += 1
        
        # 返回复杂的结果结构
        return {
            'results': results,
            'errors': errors,
            'warnings': warnings,
            'statistics': {
                'processed_count': processed_count,
                'error_count': error_count,
                'warning_count': warning_count,
                'total_input_items': len(input_data),
                'success_rate': processed_count / len(input_data) if input_data else 0
            },
            'metadata': {
                'processing_time': 0,  # 应该记录实际处理时间
                'configuration': {
                    'process_flags': process_flags,
                    'output_options': output_options,
                    'error_handling_mode': error_handling_mode
                }
            }
        }
    
    def _validate_item(self, item, rule):
        return True
    
    def _validate_single_item(self, item):
        return True
    
    def _apply_transformation(self, data, rule):
        return data
    
    def _check_criteria(self, item, criteria):
        return True
    
    def _process_single_item(self, item, settings):
        return item
    
    def _log_item_processing(self, original, processed, index):
        pass
    
    def _sort_results(self, results, options):
        return results
    
    def _format_output(self, results, options):
        return results


# 全局变量（不推荐的做法）
global_counter = 0
global_cache = {}
global_config = {
    'setting1': 'value1',
    'setting2': 'value2'
}


def function_with_no_comments_and_bad_naming(x, y, z):
    a = x + y
    b = a * z
    c = b / 2
    d = c ** 2
    return d


def duplicated_logic_function_1(data_list):
    result = []
    for item in data_list:
        if item.get('active'):
            processed = {
                'id': item.get('id'),
                'name': item.get('name'),
                'status': 'processed'
            }
            result.append(processed)
    return result


def duplicated_logic_function_2(input_items):
    output = []
    for element in input_items:
        if element.get('active'):
            transformed = {
                'id': element.get('id'),
                'name': element.get('name'),
                'status': 'processed'
            }
            output.append(transformed)
    return output


def function_without_error_handling(file_path):
    # 这个函数没有任何错误处理
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    result = data['important_key']
    return result['nested_value']
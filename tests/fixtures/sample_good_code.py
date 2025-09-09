"""
测试用的示例好代码

这个文件展示了良好的代码质量实践。
"""

from typing import List, Dict, Optional, Union
import logging
from dataclasses import dataclass


@dataclass
class User:
    """
    用户数据类
    
    Attributes:
        user_id: 用户ID
        username: 用户名
        email: 电子邮箱
        is_active: 是否激活
    """
    user_id: int
    username: str
    email: str
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Union[int, str, bool]]:
        """
        将用户对象转换为字典
        
        Returns:
            Dict[str, Union[int, str, bool]]: 用户信息字典
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active
        }


class UserService:
    """
    用户服务类
    
    提供用户相关的业务逻辑操作。
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化用户服务
        
        Args:
            logger: 日志记录器，可选
        """
        self.logger = logger or logging.getLogger(__name__)
        self._users: Dict[int, User] = {}
    
    def create_user(self, username: str, email: str) -> Optional[User]:
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 电子邮箱
            
        Returns:
            Optional[User]: 创建的用户对象，如果失败则返回None
        """
        try:
            if self._is_valid_username(username) and self._is_valid_email(email):
                user_id = self._generate_user_id()
                user = User(user_id=user_id, username=username, email=email)
                self._users[user_id] = user
                
                self.logger.info(f"成功创建用户: {username}")
                return user
            else:
                self.logger.warning(f"无效的用户名或邮箱: {username}, {email}")
                return None
                
        except Exception as e:
            self.logger.error(f"创建用户时发生错误: {e}")
            return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        return self._users.get(user_id)
    
    def get_active_users(self) -> List[User]:
        """
        获取所有激活用户
        
        Returns:
            List[User]: 激活用户列表
        """
        return [user for user in self._users.values() if user.is_active]
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        停用用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作是否成功
        """
        user = self.get_user(user_id)
        if user:
            user.is_active = False
            self.logger.info(f"已停用用户: {user.username}")
            return True
        else:
            self.logger.warning(f"用户不存在: {user_id}")
            return False
    
    def _is_valid_username(self, username: str) -> bool:
        """
        验证用户名有效性
        
        Args:
            username: 用户名
            
        Returns:
            bool: 用户名是否有效
        """
        return len(username) >= 3 and username.isalnum()
    
    def _is_valid_email(self, email: str) -> bool:
        """
        验证邮箱有效性
        
        Args:
            email: 电子邮箱
            
        Returns:
            bool: 邮箱是否有效
        """
        return '@' in email and '.' in email
    
    def _generate_user_id(self) -> int:
        """
        生成新的用户ID
        
        Returns:
            int: 新的用户ID
        """
        return max(self._users.keys(), default=0) + 1


def calculate_average(numbers: List[Union[int, float]]) -> float:
    """
    计算数字列表的平均值
    
    Args:
        numbers: 数字列表
        
    Returns:
        float: 平均值
        
    Raises:
        ValueError: 如果列表为空
        TypeError: 如果列表包含非数字类型
    """
    if not numbers:
        raise ValueError("数字列表不能为空")
    
    try:
        total = sum(numbers)
        return total / len(numbers)
    except TypeError as e:
        raise TypeError(f"列表必须包含数字类型: {e}")


def process_user_data(users: List[User], filter_active: bool = True) -> List[Dict[str, Union[int, str, bool]]]:
    """
    处理用户数据
    
    Args:
        users: 用户列表
        filter_active: 是否只返回激活用户
        
    Returns:
        List[Dict[str, Union[int, str, bool]]]: 处理后的用户数据字典列表
    """
    if filter_active:
        users = [user for user in users if user.is_active]
    
    return [user.to_dict() for user in users]
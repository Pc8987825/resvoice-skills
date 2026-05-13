"""
环境检测与依赖管理模块

提供环境检查、依赖自动安装、结构化错误报告等功能
"""

import sys
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ErrorType(Enum):
    """错误类型枚举"""
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    MISSING_FFMPEG = "MISSING_FFMPEG"
    FFMPEG_NO_AMR = "FFMPEG_NO_AMR"
    NETWORK_ERROR = "NETWORK_ERROR"
    UNKNOWN = "UNKNOWN"


@dataclass
class EnvironmentCheckResult:
    """环境检测结果"""
    ready: bool                           # 是否就绪
    python_version_ok: bool               # Python 版本是否满足
    dependencies_ready: bool              # 依赖是否就绪
    ffmpeg_ready: bool                    # ffmpeg 是否就绪
    ffmpeg_supports_amr: bool             # ffmpeg 是否支持 AMR
    missing_deps: List[str]               # 缺失的依赖列表
    missing_system_deps: List[str]        # 缺失的系统依赖
    errors: List[Dict]                    # 错误详情列表
    warnings: List[str]                   # 警告列表
    auto_fixable: bool                    # 是否可以自动修复
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class SkillError:
    """结构化错误信息"""
    success: bool = False
    error_type: str = ""
    message: str = ""
    fix_command: str = ""
    auto_fixable: bool = False
    details: Dict = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {
            "success": self.success,
            "error_type": self.error_type,
            "message": self.message,
            "fix_command": self.fix_command,
            "auto_fixable": self.auto_fixable,
        }
        if self.details:
            result["details"] = self.details
        return result


class DependencyManager:
    """依赖管理器"""
    
    REQUIRED_PACKAGES = {
        "edge_tts": "edge-tts>=7.0.0",
        "gtts": "gTTS>=2.5.0",
        "requests": "requests>=2.31.0",
    }
    
    OPTIONAL_PACKAGES = {
        "pyttsx3": "pyttsx3>=2.90",
    }
    
    @classmethod
    def check_dependencies(cls) -> Dict[str, bool]:
        """检查依赖状态"""
        status = {}
        
        for module_name, _ in cls.REQUIRED_PACKAGES.items():
            status[module_name] = cls._check_module(module_name)
        
        for module_name, _ in cls.OPTIONAL_PACKAGES.items():
            status[module_name] = cls._check_module(module_name)
        
        return status
    
    @classmethod
    def _check_module(cls, module_name: str) -> bool:
        """检查单个模块是否存在"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    @classmethod
    def get_missing_deps(cls) -> List[str]:
        """获取缺失的依赖列表"""
        status = cls.check_dependencies()
        missing = []
        
        for module_name, installed in status.items():
            if not installed and module_name in cls.REQUIRED_PACKAGES:
                missing.append(cls.REQUIRED_PACKAGES[module_name])
        
        return missing
    
    @classmethod
    def auto_install(cls, packages: Optional[List[str]] = None) -> Dict:
        """
        自动安装依赖
        
        Args:
            packages: 要安装的包列表，None 则安装所有缺失的依赖
        
        Returns:
            安装结果字典
        """
        if packages is None:
            packages = cls.get_missing_deps()
        
        if not packages:
            return {
                "success": True,
                "message": "所有依赖已安装",
                "installed": []
            }
        
        results = {
            "success": True,
            "message": "",
            "installed": [],
            "failed": []
        }
        
        for package in packages:
            try:
                # 提取包名（去掉版本号）
                pkg_name = package.split(">=")[0].split("==")[0]
                
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package, "-q"],
                    check=True,
                    capture_output=True
                )
                
                # 验证安装
                if cls._check_module(pkg_name.replace("-", "_").lower()):
                    results["installed"].append(package)
                else:
                    results["failed"].append(package)
            except subprocess.CalledProcessError as e:
                results["failed"].append(package)
                results["success"] = False
        
        if results["failed"]:
            results["success"] = False
            results["message"] = f"安装失败: {', '.join(results['failed'])}"
        else:
            results["message"] = f"成功安装: {', '.join(results['installed'])}"
        
        return results


class EnvironmentChecker:
    """环境检查器"""
    
    @classmethod
    def check_ffmpeg(cls) -> Dict:
        """检查 ffmpeg 状态"""
        result = {
            "installed": False,
            "supports_amr": False,
            "path": None,
            "version": None
        }
        
        try:
            # 检查 ffmpeg 是否存在
            proc = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True
            )
            
            if proc.returncode == 0:
                result["installed"] = True
                # 获取版本
                first_line = proc.stdout.split('\n')[0]
                result["version"] = first_line
                
                # 检查 AMR 支持
                encoders_proc = subprocess.run(
                    ["ffmpeg", "-encoders"],
                    capture_output=True,
                    text=True
                )
                
                if "amr_nb" in encoders_proc.stdout or "libopencore_amrnb" in encoders_proc.stdout:
                    result["supports_amr"] = True
        
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        return result
    
    @classmethod
    def check_python_version(cls) -> bool:
        """检查 Python 版本"""
        return sys.version_info >= (3, 9)
    
    @classmethod
    def full_check(cls, auto_install_deps: bool = False) -> EnvironmentCheckResult:
        """
        完整环境检查
        
        Args:
            auto_install_deps: 是否自动安装缺失的依赖
        
        Returns:
            EnvironmentCheckResult 检查结果
        """
        errors = []
        warnings = []
        missing_deps = []
        missing_system_deps = []
        
        # 1. 检查 Python 版本
        python_ok = cls.check_python_version()
        if not python_ok:
            errors.append({
                "type": ErrorType.UNKNOWN.value,
                "message": "Python 版本过低，需要 3.9+"
            })
        
        # 2. 检查依赖
        dep_manager = DependencyManager()
        deps_status = dep_manager.check_dependencies()
        
        for module_name, installed in deps_status.items():
            if not installed:
                if module_name in dep_manager.REQUIRED_PACKAGES:
                    missing_deps.append(dep_manager.REQUIRED_PACKAGES[module_name])
                elif module_name in dep_manager.OPTIONAL_PACKAGES:
                    warnings.append(f"可选依赖未安装: {module_name}")
        
        # 尝试自动安装
        if missing_deps and auto_install_deps:
            install_result = dep_manager.auto_install(missing_deps)
            if install_result["success"]:
                missing_deps = []  # 安装成功，清空缺失列表
            else:
                errors.append({
                    "type": ErrorType.MISSING_DEPENDENCY.value,
                    "message": f"自动安装失败: {install_result['message']}",
                    "fix_command": f"{sys.executable} -m pip install " + " ".join(missing_deps)
                })
        
        # 3. 检查 ffmpeg
        ffmpeg_status = cls.check_ffmpeg()
        ffmpeg_ready = ffmpeg_status["installed"]
        ffmpeg_amr = ffmpeg_status["supports_amr"]
        
        if not ffmpeg_ready:
            missing_system_deps.append("ffmpeg")
            errors.append({
                "type": ErrorType.MISSING_FFMPEG.value,
                "message": "未找到 ffmpeg，请安装",
                "fix_command": "# Windows: winget install Gyan.FFmpeg\n# macOS: brew install ffmpeg\n# Ubuntu: sudo apt-get install ffmpeg"
            })
        elif not ffmpeg_amr:
            warnings.append("ffmpeg 不支持 AMR 编码，企业微信语音可能无法发送")
        
        # 4. 判断是否就绪
        deps_ready = len(missing_deps) == 0
        ready = python_ok and deps_ready
        
        # 5. 判断是否可自动修复
        auto_fixable = len(missing_deps) > 0 and len(missing_system_deps) == 0
        
        return EnvironmentCheckResult(
            ready=ready,
            python_version_ok=python_ok,
            dependencies_ready=deps_ready,
            ffmpeg_ready=ffmpeg_ready,
            ffmpeg_supports_amr=ffmpeg_amr,
            missing_deps=missing_deps,
            missing_system_deps=missing_system_deps,
            errors=errors,
            warnings=warnings,
            auto_fixable=auto_fixable
        )


def check_environment(auto_install: bool = False) -> Dict:
    """
    环境检查入口函数
    
    Args:
        auto_install: 是否尝试自动安装缺失的依赖
    
    Returns:
        检查结果字典
    """
    checker = EnvironmentChecker()
    result = checker.full_check(auto_install_deps=auto_install)
    return result.to_dict()


def ensure_dependencies() -> Optional[SkillError]:
    """
    确保依赖已安装，返回错误信息（如果有）
    
    Returns:
        如果有错误返回 SkillError，否则返回 None
    """
    checker = EnvironmentChecker()
    result = checker.full_check(auto_install_deps=True)
    
    if result.ready:
        return None
    
    # 构建错误信息
    if result.missing_deps:
        return SkillError(
            error_type=ErrorType.MISSING_DEPENDENCY.value,
            message=f"缺少依赖: {', '.join(result.missing_deps)}",
            fix_command=f"{sys.executable} -m pip install " + " ".join(result.missing_deps),
            auto_fixable=len(result.missing_system_deps) == 0,
            details={
                "missing_deps": result.missing_deps,
                "missing_system_deps": result.missing_system_deps
            }
        )
    
    if result.missing_system_deps:
        return SkillError(
            error_type=ErrorType.MISSING_FFMPEG.value,
            message=f"缺少系统依赖: {', '.join(result.missing_system_deps)}",
            fix_command="请安装 ffmpeg",
            auto_fixable=False,
            details={"missing": result.missing_system_deps}
        )
    
    return SkillError(
        error_type=ErrorType.UNKNOWN.value,
        message="环境检查失败",
        auto_fixable=False
    )


# 向后兼容的快捷函数
def check_deps() -> Dict:
    """快捷检查依赖状态"""
    return DependencyManager.check_dependencies()


def install_deps() -> Dict:
    """快捷安装依赖"""
    return DependencyManager.auto_install()

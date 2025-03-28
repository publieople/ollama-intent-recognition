"""
应用程序主入口模块，提供应用程序的主要功能。
"""
import sys
import logging
from typing import Optional, Dict, Any, List

from src.config.settings import settings
from src.ollama_client import OllamaClient
from src.services.prompt_processor import PromptProcessorService
from src.services.report_service import ReportService
from src.utils.prompt_utils import (
    load_prompts_from_file, load_prompts_from_json, 
    load_prompts_from_inputs_folder, load_system_prompt,
    get_default_prompts
)
from src.utils.report_utils import open_report_in_browser
from src.cli.logging_setup import setup_logging


class OllamaIntentApp:
    """Ollama对话意图识别应用程序类"""
    
    def __init__(self, args: Dict[str, Any]):
        """初始化应用程序
        
        Args:
            args: 命令行参数字典
        """
        self.args = args
        self.logger = logging.getLogger(__name__)
        self.prompt_processor: Optional[PromptProcessorService] = None
        self.system_prompt: str = ""
        self.prompts: List[str] = []
        self.dataset_file: Optional[str] = None
    
    def setup(self) -> None:
        """设置应用程序"""
        # 配置日志
        setup_logging(self.args.log_level, self.args.log_file)
        
        # 打印欢迎信息
        self._print_welcome_message()
    
    def _print_welcome_message(self) -> None:
        """打印欢迎信息"""
        self.logger.info("=" * 50)
        self.logger.info("Ollama对话意图识别工具")
        self.logger.info("=" * 50)
        self.logger.info(f"当前配置: ")
        self.logger.info(f"  - API URL: {settings.api_url}")
        self.logger.info(f"  - 模型: {settings.model_name}")
        self.logger.info(f"  - 温度: {settings.temperature}")
        self.logger.info(f"  - Top-P: {settings.top_p}")
        self.logger.info(f"  - 精确度偏差: {settings.precision_bias} (正值降低假正例)")
        self.logger.info(f"  - 输出目录: {settings.output_dir}")
        self.logger.info("=" * 50)
    
    def test_connection(self) -> bool:
        """测试与Ollama API的连接
        
        Returns:
            连接是否成功
        """
        self.logger.info(f"测试与Ollama API的连接: {settings.api_url}")
        self.logger.info(f"测试模型: {settings.model_name}")
        
        client = OllamaClient(settings.api_url)
        available, error_msg = client.check_model_available(settings.model_name)
        
        if available:
            self.logger.info(f"成功连接到Ollama API，模型 {settings.model_name} 可用")
            return True
        else:
            self.logger.error(f"无法连接到Ollama API: {error_msg}")
            return False
    
    def load_prompts(self) -> bool:
        """加载系统提示词和提示词列表
        
        Returns:
            是否成功加载
        """
        # 加载系统提示词
        self.system_prompt = load_system_prompt(self.args.system_prompt_file)
        self.logger.info(f"系统提示词长度: {len(self.system_prompt)} 字符")
        
        # 根据不同的输入源加载提示词
        if self.args.dataset_file:
            # 直接从特定数据集文件加载
            self.prompts = load_prompts_from_json(self.args.dataset_file)
            if self.prompts:
                self.logger.info(f"已从数据集文件加载 {len(self.prompts)} 个提示词: {self.args.dataset_file}")
                self.dataset_file = self.args.dataset_file
            else:
                self.logger.warning("从数据集文件加载提示词失败，使用默认提示词列表")
                self.prompts = get_default_prompts()
        elif self.args.inputs_folder:
            self.prompts = load_prompts_from_inputs_folder(self.args.inputs_folder)
            if not self.prompts:
                self.logger.warning("从inputs文件夹加载提示词失败，使用默认提示词列表")
                self.prompts = get_default_prompts()
            else:
                self.logger.info(f"已从inputs文件夹加载 {len(self.prompts)} 个提示词")
        elif self.args.prompts_file:
            self.prompts = load_prompts_from_file(self.args.prompts_file)
            if not self.prompts:
                self.logger.warning("从文件加载提示词失败，使用默认提示词列表")
                self.prompts = get_default_prompts()
            else:
                self.logger.info(f"已从文件加载 {len(self.prompts)} 个提示词: {self.args.prompts_file}")
        else:
            self.prompts = get_default_prompts()
            self.logger.info("使用默认提示词列表")
        
        return len(self.prompts) > 0
    
    def process_prompts(self) -> Dict[str, Any]:
        """处理提示词
        
        Returns:
            处理结果
        """
        # 创建处理服务
        self.prompt_processor = PromptProcessorService()
        
        # 处理提示词
        result = self.prompt_processor.process_prompts(
            model_name=settings.model_name,
            system_prompt=self.system_prompt,
            prompts=self.prompts
        )
        
        # 添加日志输出
        self.logger.info(f"处理完成，结果包含 {len(result.get('summary', []))} 个样本")
        self.logger.info(f"是否生成报告: {settings.generate_report}")
        
        return result
    
    def generate_report(self, result: Dict[str, Any]) -> None:
        """生成报告
        
        Args:
            result: 处理结果
        """
        if not settings.generate_report:
            self.logger.info("未生成HTML报告（已禁用）")
            return
        
        summary = result.get("summary", [])
        metrics = result.get("metrics", {})
        
        # 添加详细的日志输出
        self.logger.info("=" * 50)
        self.logger.info("报告生成信息:")
        self.logger.info(f"  - 摘要包含 {len(summary)} 个样本")
        self.logger.info(f"  - 评估指标: {metrics}")
        self.logger.info(f"  - 输出目录: {settings.output_dir}")
        self.logger.info(f"  - 是否生成报告: {settings.generate_report}")
        self.logger.info(f"  - 是否自动打开报告: {settings.open_report}")
        self.logger.info("=" * 50)
        
        # 创建报告服务
        report_service = ReportService()
        
        # 生成并保存HTML报告
        report_file = report_service.generate_html_report(
            summary=summary,
            system_prompt=self.system_prompt,
            metrics=metrics,
            dataset_file=self.dataset_file
        )
        
        if report_file:
            self.logger.info(f"报告已生成: {report_file}")
            if settings.open_report:
                self.logger.info("正在浏览器中打开报告...")
                open_report_in_browser(report_file)
        else:
            self.logger.error("报告生成失败")
    
    def run(self) -> int:
        """运行应用程序
        
        Returns:
            退出代码
        """
        # 设置应用程序
        self.setup()
        
        # 测试连接
        if self.args.test_connection:
            if self.test_connection():
                self.logger.info("连接测试成功")
                return 0
            else:
                self.logger.error("连接测试失败，请检查Ollama服务是否正在运行")
                return 1
        
        # 加载提示词
        if not self.load_prompts():
            self.logger.error("加载提示词失败")
            return 1
        
        # 处理提示词
        result = self.process_prompts()
        
        # 生成报告
        self.generate_report(result)
        
        self.logger.info("处理完成")
        return 0 
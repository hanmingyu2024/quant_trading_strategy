"""
开源模型下载管理器

功能:
- 下载指定的开源模型
- 管理模型版本
- 检查模型完整性
- 显示下载进度

作者: Han Mingyu
邮箱: 13364694109ai@gmail.com
"""

import os
import json
from datetime import datetime
import oss2
from transformers import AutoModel, AutoTokenizer
import logging
from .config import OSS_CONFIG
from .utils import setup_logging

class ModelDownloader:
    def __init__(self, oss_access_key_id: str = None,
                 oss_access_key_secret: str = None,
                 oss_bucket_name: str = None,
                 oss_endpoint: str = None):
        # 使用环境变量或传入的配置
        self.base_path = "models"
        self.supported_models = {
            "chatglm3": "THUDM/chatglm3-6b",
            "llama2": "meta-llama/Llama-2-7b-chat-hf",
            "baichuan": "baichuan-inc/Baichuan2-13B-Chat",
            "qwen": "Qwen/Qwen-7B-Chat",
            "bloomz": "bigscience/bloomz-7b1"
        }

        # 初始化日志
        self.logger = setup_logging()

        # 初始化OSS配置
        self.oss_access_key_id = oss_access_key_id or OSS_CONFIG['access_key_id']
        self.oss_access_key_secret = oss_access_key_secret or OSS_CONFIG['access_key_secret']
        self.oss_bucket_name = oss_bucket_name or OSS_CONFIG['bucket_name']
        self.oss_endpoint = oss_endpoint or OSS_CONFIG['endpoint']

        # 初始化OSS客户端
        self.auth = oss2.Auth(self.oss_access_key_id, self.oss_access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.oss_endpoint, self.oss_bucket_name)
        self.oss_prefix = "models/"

    def download_model(self, model_name: str, use_auth_token: str = None):
        """下载模型并上传到OSS"""
        if model_name not in self.supported_models:
            self.logger.error(f"不支持的模型: {model_name}")
            return False

        model_path = self.supported_models[model_name]
        save_path = os.path.join(self.base_path, model_name)

        try:
            self.logger.info(f"开始下载模型: {model_name}")
            os.makedirs(save_path, exist_ok=True)

            # 下载模型和分词器
            model = AutoModel.from_pretrained(
                model_path,
                trust_remote_code=True,
                use_auth_token=use_auth_token,
                cache_dir=save_path
            )

            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                use_auth_token=use_auth_token,
                cache_dir=save_path
            )

            # 保存模型配置
            self._save_model_config(model_name, save_path)

            # 上传到OSS
            self._upload_to_oss(save_path, model_name)

            self.logger.info(f"模型 {model_name} 下载并上传完成")
            return True

        except Exception as e:
            self.logger.error(f"处理失败: {str(e)}")
            return False

    def _upload_to_oss(self, local_path: str, model_name: str):
        """上传模型文件到OSS"""
        self.logger.info(f"开始上传模型到OSS: {model_name}")

        for root, _, files in os.walk(local_path):
            for file in files:
                local_file = os.path.join(root, file)
                # 构建OSS对象键
                relative_path = os.path.relpath(local_file, local_path)
                oss_key = f"{self.oss_prefix}{model_name}/{relative_path}"

                # 上传文件到OSS
                self.logger.info(f"上传文件: {relative_path}")
                self.bucket.put_object_from_file(oss_key, local_file)

    def _save_model_config(self, model_name: str, save_path: str):
        """保存模型配置"""
        config = {
            "model_name": model_name,
            "huggingface_path": self.supported_models[model_name],
            "download_time": str(datetime.now()),
            "local_path": save_path
        }

        config_path = os.path.join(save_path, "model_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def verify_model(self, model_name: str, check_oss: bool = True) -> bool:
        """验证模型完整性（本地和OSS）"""
        # 检查本地模型
        local_valid = super().verify_model(model_name)

        if check_oss:
            try:
                # 检查OSS中的模型文件
                oss_prefix = f"{self.oss_prefix}{model_name}/"
                exist = self.bucket.object_exists(f"{oss_prefix}model_config.json")

                if not exist:
                    self.logger.error(f"OSS中未找到模型: {model_name}")
                    return False

                self.logger.info(f"OSS中的模型 {model_name} 验证成功")
                return True

            except Exception as e:
                self.logger.error(f"OSS模型验证失败: {str(e)}")
                return False

        return local_valid

    def list_downloaded_models(self):
        """列出已下载的模型"""
        if not os.path.exists(self.base_path):
            self.logger.info("模型目录为空")
            return []

        models = []
        for model_name in os.listdir(self.base_path):
            config_path = os.path.join(
                self.base_path,
                model_name,
                "model_config.json"
            )
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                models.append(config)

        return models

def main():
    # OSS配置
    oss_config = {
        "oss_access_key_id": "your_access_key_id",
        "oss_access_key_secret": "your_access_key_secret",
        "oss_bucket_name": "your_bucket_name",
        "oss_endpoint": "your_endpoint"
    }

    # 创建下载器实例
    downloader = ModelDownloader(**oss_config)

    # 下载指定模型
    model_name = "chatglm3"  # 或其他支持的模型名称

    # 如果需要认证token(某些模型需要)
    auth_token = "your_huggingface_token"  # 替换为你的token

    # 开始下载
    success = downloader.download_model(model_name, auth_token)

    if success:
        # 验证下载
        if downloader.verify_model(model_name):
            print(f"模型 {model_name} 下载并验证成功!")

    # 列出所有已下载的模型
    models = downloader.list_downloaded_models()
    print("\n已下载的模型:")
    for model in models:
        print(f"- {model['model_name']}")

if __name__ == "__main__":
    main()

import coverage
import unittest
import time
import json
import psutil
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from backend.tests.test_base import TestBase
from backend.tests.test_config import test_config
from backend.app.utils.logger import get_logger

class CoverageRunner(TestBase):
    """覆盖率测试运行器"""
    
    def __init__(self):
        super().__init__()
        self.cov = coverage.Coverage(
            branch=True,
            source=test_config.test_config['coverage_source'],
            omit=test_config.test_config['coverage_omit']
        )
        self.start_time = None
        self.results: Dict = {}
        self.logger = get_logger('coverage_test')

    def start(self):
        """开始测试"""
        try:
            self.start_time = time.time()
            self.cov.start()
            self.logger.info("=== 开始覆盖率测试 ===")
            
            # 检查系统资源
            self.check_test_resources()
            
            # 准备报告目录
            test_config.REPORT_DIR.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            self.logger.error(f"测试启动失败: {e}")
            raise

    def run_test_suite(self, test_dir: str) -> Dict:
        """运行单个测试套件"""
        suite_result = {
            'name': test_dir,
            'start_time': time.time()
        }
        
        try:
            # 构建测试套件路径
            suite_path = Path('backend/tests') / test_dir
            self.logger.info(f"运行测试套件: {suite_path}")
            
            # 发现并运行测试
            suite = unittest.TestLoader().discover(
                str(suite_path),
                pattern='test_*.py'
            )
            
            # 使用自定义测试运行器
            runner = unittest.TextTestRunner(
                verbosity=2,
                stream=open(test_config.LOG_DIR / f"{test_dir}_tests.log", 'w')
            )
            result = runner.run(suite)
            
            # 记录结果
            suite_result.update({
                'total': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped),
                'success': result.wasSuccessful(),
                'duration': time.time() - suite_result['start_time']
            })
            
            # 记录失败的测试详情
            if not result.wasSuccessful():
                failures_details = []
                for failure in result.failures + result.errors:
                    failures_details.append({
                        'test': str(failure[0]),
                        'error': str(failure[1])
                    })
                suite_result['failures_details'] = failures_details
            
            return suite_result
            
        except Exception as e:
            self.logger.error(f"测试套件 {test_dir} 执行失败: {e}")
            suite_result.update({
                'error': str(e),
                'duration': time.time() - suite_result['start_time']
            })
            return suite_result

    def run_all_tests(self):
        """运行所有测试"""
        self.logger.info("开始运行所有测试套件")
        
        with ThreadPoolExecutor(max_workers=test_config.CPU_LIMIT) as executor:
            futures = [
                executor.submit(self.run_test_suite, test_dir)
                for test_dir in test_config.test_config['test_dirs']
            ]
            
            self.results = {
                f.result()['name']: f.result()
                for f in futures
            }

    def generate_report(self):
        """生成测试报告"""
        try:
            self.cov.stop()
            duration = time.time() - self.start_time
            
            # 生成HTML报告
            html_dir = test_config.REPORT_DIR / 'html'
            self.cov.html_report(directory=str(html_dir))
            
            # 收集系统信息
            system_info = {
                'platform': sys.platform,
                'python_version': sys.version,
                'memory_usage': f"{psutil.Process().memory_percent():.1f}%",
                'cpu_usage': f"{psutil.cpu_percent():.1f}%",
                'start_time': time.strftime('%Y-%m-%d %H:%M:%S', 
                                          time.localtime(self.start_time)),
                'duration': f"{duration:.2f}秒"
            }
            
            # 收集覆盖率数据
            coverage_data = {
                'total_statements': self.cov.get_data().n_statements,
                'missing_statements': len(self.cov.get_data().missing_lines()),
                'coverage_percent': self.cov.report(show_missing=False)
            }
            
            # 生成完整报告数据
            report_data = {
                'system_info': system_info,
                'test_results': self.results,
                'coverage_data': coverage_data,
                'summary': {
                    'total_tests': sum(r.get('total', 0) for r in self.results.values()),
                    'failed_tests': sum(r.get('failures', 0) for r in self.results.values()),
                    'error_tests': sum(r.get('errors', 0) for r in self.results.values()),
                    'skipped_tests': sum(r.get('skipped', 0) for r in self.results.values())
                }
            }
            
            # 保存JSON报告
            json_file = test_config.REPORT_DIR / 'coverage_summary.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # 输出报告位置
            self.logger.info(f"\n=== 测试报告已生成 ===")
            self.logger.info(f"HTML报告: {html_dir}/index.html")
            self.logger.info(f"JSON报告: {json_file}")
            
            # 输出测试结果摘要
            self._print_summary(report_data)
            
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            raise

    def _print_summary(self, report_data):
        """打印测试摘要"""
        self.logger.info("\n=== 测试结果摘要 ===")
        summary = report_data['summary']
        self.logger.info(f"总测试数: {summary['total_tests']}")
        self.logger.info(f"失败: {summary['failed_tests']}")
        self.logger.info(f"错误: {summary['error_tests']}")
        self.logger.info(f"跳过: {summary['skipped_tests']}")
        self.logger.info(f"覆盖率: {report_data['coverage_data']['coverage_percent']:.1f}%")

def main():
    """主函数"""
    runner = CoverageRunner()
    
    try:
        runner.start()
        runner.run_all_tests()
        runner.generate_report()
        
    except KeyboardInterrupt:
        runner.logger.warning("\n测试被手动中断!")
    except Exception as e:
        runner.logger.error(f"\n测试过程出现错误: {str(e)}")
    finally:
        runner.logger.info("\n测试完成!")

if __name__ == "__main__":
    main() 
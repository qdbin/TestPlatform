"""
运行所有测试：
    python run_tests.py

运行特定测试：
    python run_tests.py unit
    python run_tests.py integration
    python run_tests.py eval
    python run_tests.py smoke
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """运行命令并打印结果"""
    print("\n" + "=" * 60)
    print(f"运行: {description}")
    print("=" * 60)
    print(f"命令: {cmd}\n")

    result = subprocess.run(cmd, shell=True, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """主函数"""
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"

    print("\n" + "=" * 60)
    print("AI服务测试套件")
    print("=" * 60)
    print(f"测试类型: {test_type}")

    exit_codes = []

    if test_type in ["all", "unit"]:
        # 运行单元测试
        code = run_command("python -m pytest tests/unit/ -v --tb=short -x", "单元测试")
        exit_codes.append(code)

    if test_type in ["all", "integration"]:
        # 运行集成测试
        code = run_command(
            "python -m pytest tests/integration/ -v --tb=short -x", "集成测试"
        )
        exit_codes.append(code)

    if test_type in ["all", "smoke"]:
        # 运行冒烟测试
        code = run_command(
            "python tests/integration/test_smoke_requests.py", "冒烟测试"
        )
        exit_codes.append(code)

    if test_type in ["all", "eval"]:
        # 运行评估测试
        code = run_command(
            "python -m pytest evals/test_rag_eval.py evals/test_agent_eval.py -v --tb=short -m 'not langsmith'",
            "评估测试 (不含LangSmith)",
        )
        exit_codes.append(code)

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    if all(code == 0 for code in exit_codes):
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

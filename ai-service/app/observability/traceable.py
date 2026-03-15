"""
LangSmith追踪装饰器模块

职责：
    1. 提供统一的LangSmith追踪装饰器
    2. 自动记录函数调用和参数
    3. 支持嵌套追踪

使用说明：
    使用 @traceable 装饰器标记需要追踪的函数：

    @traceable(name="my_function", run_type="chain")
    def my_function(arg1, arg2):
        return result

    run_type 类型：
    - llm: LLM调用
    - chain: 链式调用
    - tool: 工具调用
    - retriever: 检索器调用
    - embedding: Embedding调用
"""

from functools import wraps
from typing import Any, Callable, Optional

from langsmith import trace

from app.config import config


def traceable(
    name: Optional[str] = None,
    run_type: str = "chain",
    tags: Optional[list] = None,
):
    """
    LangSmith追踪装饰器

    为函数添加LangSmith追踪能力，自动记录：
    - 函数名和参数
    - 执行时间
    - 返回值
    - 异常信息

    @param name: 追踪名称（默认为函数名）
    @param run_type: 运行类型（llm/chain/tool/retriever/embedding）
    @param tags: 标签列表
    @return: 装饰器函数

    使用示例：
        @traceable(name="rag_search", run_type="retriever")
        def search(query: str):
            return results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 如果未启用追踪，直接执行
            if not config.langsmith_tracing:
                return func(*args, **kwargs)

            # 构建追踪名称
            trace_name = name or func.__name__

            # 构建输入参数
            inputs = {}
            if args:
                inputs["args"] = args
            if kwargs:
                inputs["kwargs"] = kwargs

            # 使用LangSmith trace上下文管理器
            with trace(
                name=trace_name,
                run_type=run_type,
                inputs=inputs,
                tags=tags or [],
            ) as run:
                try:
                    result = func(*args, **kwargs)
                    # 记录输出
                    if run:
                        run.outputs = {"result": result}
                    return result
                except Exception as e:
                    # 记录异常
                    if run:
                        run.error = str(e)
                    raise

        return wrapper
    return decorator


if __name__ == "__main__":
    """追踪装饰器调试"""
    print("=" * 60)
    print("LangSmith追踪装饰器调试")
    print("=" * 60)

    # 测试追踪装饰器
    print("\n1. 测试追踪装饰器:")

    @traceable(name="test_function", run_type="chain")
    def test_function(a: int, b: int) -> int:
        """测试函数"""
        return a + b

    result = test_function(1, 2)
    print(f"   函数结果: {result}")
    print(f"   追踪状态: {'已启用' if config.langsmith_tracing else '未启用'}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)

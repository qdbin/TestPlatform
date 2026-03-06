# 调试文件目录

此目录用于临时调试和测试文件，请勿提交到版本控制。

## 已清理的文件

以下调试文件已被清理：
- check_mysql.py
- debug_ai.py
- debug_config.py
- debug_frontend.py
- debug_frontend_ai.py
- debug_llm.py
- fix_mysql.py
- fix_mysql2.py
- test_ai_debug.py
- test_ai_direct.py
- test_api*.py
- test_backend_ai.py

## 推荐的测试方式

1. **后端单元测试**：在 `platform-backend/src/test/java/com/autotest/` 目录下编写JUnit测试
2. **AI服务测试**：在 `ai-service/tests/` 目录下编写pytest测试
3. **前端测试**：在 `platform-frontend/tests/` 目录下编写组件测试

## 注意事项

- 临时调试文件请勿提交到Git
- 使用 `.gitignore` 排除此目录

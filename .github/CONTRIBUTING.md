# 贡献指南

## 开发流程
1. Fork 并克隆项目
2. 创建新分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 代码规范
- 遵循项目现有的代码风格
- 添加必要的测试用例
- 保持代码注释完整
- 使用 Black 进行代码格式化
- 通过 Flake8 代码检查
- 变量和函数命名要有意义且符合 Python 规范

## 提交 PR 前的检查项
- [ ] 代码已经过测试
- [ ] 所有测试用例通过
- [ ] 代码符合项目规范
- [ ] 已更新相关文档
- [ ] 代码已经过 Black 格式化
- [ ] 通过 Flake8 检查
- [ ] Commit 信息清晰明确
- [ ] 已添加必要的单元测试

## 版本发布规范
- 遵循语义化版本 (Semantic Versioning)
- 重大更新：MAJOR.x.x
- 功能更新：x.MINOR.x
- 问题修复：x.x.PATCH

## 问题反馈
- 使用 GitHub Issues 提交问题
- 清晰描述问题现象
- 提供复现步骤
- 附上相关日志和截图
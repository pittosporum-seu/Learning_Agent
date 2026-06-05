# Lab Testing

这里放跨 Lab 复用的测试入口。

当前使用 Python 标准库 `unittest`，不引入额外依赖。每个 Lab 只要把测试放在自己的 `tests/` 目录下，就可以被统一发现。

从仓库根目录运行全部 Lab 测试：

```powershell
python labs/shared/testing/run_lab_tests.py
```

只运行某个 Lab：

```powershell
python labs/shared/testing/run_lab_tests.py --lab 01-strategy-intake
```

Windows 下也可以使用封装脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1
powershell -ExecutionPolicy Bypass -File scripts/run-lab-tests.ps1 -Lab 01-strategy-intake
```

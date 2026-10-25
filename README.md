# AI Infra 学习仓库

用于整理 AI 基础设施学习项目、个人笔记、阅读资料和实验记录。

当前已整理 Python 基础与并发笔记，并添加练习示例。编程语言基础笔记放在 `notes/00-foundations/编程语言基础/`，包括 [Python 学习笔记](notes/00-foundations/编程语言基础/Python学习笔记.md) 和 [Python 并发与性能分析](notes/00-foundations/编程语言基础/Python并发与性能分析.md)。

## 目录结构

```text
AI-Infra/
├── README.md                       # 仓库入口与目录说明
├── projects/                       # 按开源项目组织的学习实践
│   ├── 00-foundations/             # Python 基础、并发与性能测试练习
│   ├── 01-nano-vllm/               # 轻量推理引擎，建议从这里开始
│   ├── 02-triton/                  # GPU 算子编程
│   ├── 03-vllm/                    # 推理服务与调度
│   ├── 04-llm-c/                   # C/CUDA 训练实现
│   ├── 05-torchtitan/              # 分布式训练
│   ├── 06-llama-cpp/               # C++ 推理与量化
│   └── 07-sglang/                  # 推理缓存与服务优化
├── notes/                          # 按知识主题整理的笔记
│   ├── 00-foundations/             # Python、C++、Linux、PyTorch 基础
│   │   └── 编程语言基础/
│   │       ├── Python学习笔记.md   # 函数、类、生成器等基础知识
│   │       └── Python并发与性能分析.md # 并发模型与性能分析
│   ├── 01-gpu-cuda/                # GPU 架构、CUDA 与访存
│   ├── 02-kernels-compilers/       # Triton、算子优化与编译器
│   ├── 03-inference/               # KV Cache、推理调度与量化
│   ├── 04-distributed-training/    # 分布式训练与通信
│   ├── 05-systems/                 # 容器、资源调度与监控
│   └── 06-paper-reading/           # 论文阅读笔记
├── docs/                           # 后续的学习路线、环境与使用说明
├── resources/                      # 学习资料与链接索引
│   ├── papers/                     # 论文资料
│   ├── courses/                    # 课程资料
│   └── articles/                   # 技术文章
├── templates/                      # 后续的笔记、源码阅读与实验记录模板
├── assets/                         # 文档使用的图片与示意图
│   ├── images/
│   └── diagrams/
├── external/                       # 本地克隆的上游项目
├── data/                           # 本地数据集与测试输入
├── models/                         # 本地模型权重
└── outputs/                        # 运行日志、性能分析与临时输出
```

每个 `projects/项目名/` 下都预留：

```text
项目名/
├── src/                            # 自己编写的练习与实现
└── experiments/                    # 实验配置、复现说明与整理后的结果
```

## 放置约定

- 自己写的代码放在 `projects/项目名/src/`，原始上游仓库放在 `external/`。
- 通用知识放在 `notes/`；与具体项目绑定的实验记录放在对应的 `experiments/`。
- 文档插图放在 `assets/`；原始日志和临时输出放在 `outputs/`。
- `external/`、`data/`、`models/`、`outputs/` 的内容默认由 Git 忽略；需要长期保留的小型实验结果可以整理到对应项目目录。
- 空目录中的 `.gitkeep` 仅用于让 Git 保留目录结构，有实际内容后可以移除。
- 项目编号用于导航，后续按需要选择分支，不要求依次学完所有项目。

## 项目入口

| 本地目录 | 上游项目 |
| --- | --- |
| [01-nano-vllm](projects/01-nano-vllm/) | [GeeeekExplorer/nano-vllm](https://github.com/GeeeekExplorer/nano-vllm) |
| [02-triton](projects/02-triton/) | [triton-lang/triton](https://github.com/triton-lang/triton) |
| [03-vllm](projects/03-vllm/) | [vllm-project/vllm](https://github.com/vllm-project/vllm) |
| [04-llm-c](projects/04-llm-c/) | [karpathy/llm.c](https://github.com/karpathy/llm.c) |
| [05-torchtitan](projects/05-torchtitan/) | [pytorch/torchtitan](https://github.com/pytorch/torchtitan) |
| [06-llama-cpp](projects/06-llama-cpp/) | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) |
| [07-sglang](projects/07-sglang/) | [sgl-project/sglang](https://github.com/sgl-project/sglang) |

目录组织参考了 [AI-infra-LearningNote](https://github.com/jiajun-c/AI-infra-LearningNote) 的主题分类，以及 [ai-infra-notes](https://github.com/slowlyC/ai-infra-notes) 的实践代码与文档分区方式；具体目录按个人学习用途调整。

# 成品测试报告 — 视频反推提示词验证闭环（第 1 条样本）

日期：2026-10-18。执行：Muse（生成引擎 = Muse 自带 AI 视频生成管线，全程同一引擎同一设置）。
样本：1 条参考片（单镜头、单主体、10 秒）。本报告只证明这一条样本上的结果，不外推。

## 实验设计（生成前定死）
- 参考片由一条已知原词生成（原词封存，反推时只看画面），1280×720、24fps、10.0s。
- 打分三层，跑之前定死：①客观分 = 自研 score_pair.py（6 个归一化时刻帧对：直方图相关 + 全局 SSIM + pHash，各 1/3，满分 100；自检 ref vs ref = 100.0）；②量规分 = 看对照图按 5 轴各 20 分（主体/动作/环境/运镜构图/光线风格），评分人 = 执行 agent 本人，**非盲评**，只作辅助，结论以客观分为锚；③实测层 = 借 video-sharingan 的 analyze/compare（运镜速度、推近率、镜头时长、音频类门禁表）。
- 纪律：先测噪声底（同词 P0 生成 3 次）；每轮只改一轴；对照 = 同词 best-of-3。

## 参考片画面（反推依据）
橘猫从画面左缘侧面入画横穿木露台 → 转向镜头走近 → 坐下直视镜头 → 缓慢推近至中近景。露台是褪色浅灰褐色旧木板，盆栽以绿植为主，花园虚化、少量粉花，有小蝴蝶，暖金色斜阳、斑驳树影。

## 提示词链
- **原词（封存，仅供事后对照）**："A small orange tabby cat walks slowly across a sunlit wooden deck terrace toward the camera, then stops and sits down, flicking its tail. Low camera angle at cat height, slow push-in. Warm late-afternoon golden sunlight, potted plants and a soft green garden in the background, shallow depth of field, photorealistic, single continuous shot, about 5 seconds."（注：实际成片 10 秒且动作与原词有出入——反推对象是成片，不是原词，这正是要点。）
- **P0（只看画面反推）**："An orange tabby cat on a sunlit wooden deck terrace surrounded by potted green plants and a lush garden with pink flowers. The cat walks across the deck in side profile, then turns toward the camera, walks closer and sits down facing the camera, looking into the lens. Low camera angle at cat height, slow continuous push-in ending in a close-up of the cat's face. Warm golden afternoon sunlight, dappled leaf shadows on the wooden planks, a few butterflies fluttering in the background, shallow depth of field, photorealistic, single continuous shot, about 10 seconds."
- **P1（只改运镜轴）**：把运镜句换为 "Wide low camera angle at cat height; the cat starts small in the frame, entering from the left edge. Very slow continuous push-in; by the end the seated cat is framed in a medium close-up with head, chest and front paws visible, its head about 40 percent of the frame height, never an extreme face-filling close-up."，其余与 P0 逐字相同。
- **P2（只改环境轴）**：环境句换为褪色浅灰褐旧木板、少量陶土盆绿植、虚化绿花园＋少量粉花、蝴蝶改 "tiny distant"，运镜沿用 P1，其余不动。

## 分数
客观分（逐帧见运行记录）：
| 轮次 | 客观分 | 量规分（主/动/环/运/光） | 综合（两层均值） |
|---|---|---|---|
| P0 第 1 抽 | 42.9 | 74（18/18/12/12/14） | 58.5 |
| P0 第 2 抽 | 40.8 | 73（18/16/12/12/15） | 56.9 |
| P0 第 3 抽（对照） | 41.9 | 72（18/17/11/12/14） | 57.0 |
| P1（改运镜） | **48.4** | 78（18/17/12/16/15） | 63.2 |
| P2（改环境） | **53.0** | 79（17/14/17/16/15） | **66.0** |

- 噪声底：P0 三抽客观分 42.9 / 40.8 / 41.9，均值 41.9，极差 2.1。
- 实测层（video-sharingan compare，REF vs P2）：7 项门禁过 6 项——画幅/fps/镜头时长/ASL/推近率（9.17 vs ≤9.71 %/s）PASS；**运镜内容速度 FAIL**（P2 7.5 px/s vs 参考 57.5–77.7 px/s）；音频类 WARN（参考 sfx-only vs P2 music+sfx）。另注：sharingan 的 brief 阶段在无音乐类音频上有个 verdict 为空的崩溃 bug，analysis.json 不受影响。

## 判读
- **闭环有效（本样本）**：客观分 41.9 → 48.4 → 53.0 单调上升；P1 的 +6.5、P2 的 +11.1（对 P0 均值）都明显超过噪声极差 2.1，不是抽卡运气能解释的。
- **赢 best-of-N**：同词抽 3 次最好 42.9，闭环终局 53.0，高 +10.1。成本如实记账：闭环一侧共用 5 次生成（P0×3 含噪声与对照、P1、P2），对照侧 3 次——预算不对等，对照若也给 5 抽预计还能涨一点（未实测），但量级追不上 +10。
- **每轮改动买到了什么**：改运镜买到结尾帧（末两帧客观分 39.8/39.0 → 51.9/56.2）与量规运镜 12→16；改环境买到全帧段普涨与量规环境 12→17（浅色旧木板、盆栽稀疏化与原片对上）。

## 没闭上的缺口（下一轮 P3 的靶子）
1. 运动量不足：实测层运镜速度 FAIL——原片前段猫横穿＋推近的画面流动比 P2 强得多；P2 后半猫基本静止。
2. P2 动作轴回退：猫后半段是趴卧（loaf）不是原片的端坐，量规动作 17→14；眼睛还过于橙亮。
3. P3 处方（已定，未跑）：只改动作轴——要求猫持续向镜头走近到约 7 秒才端坐、坐姿保持直立、尾巴摆动，压住"趴卧"表述。本条消息的 6 条生成额度已用满，P3 留到下一轮。

## 引擎层面的保留意见
- 本次生成引擎是 Muse 媒体管线，其子代理会自行扩写提示词、且不能固定 seed——提示词文本不是唯一变量，噪声底（极差 2.1）里包含这部分。换到可固定 seed、原文直达的 API（Seedance/Kling/Veo）上，闭环的控制力只会更强，但本次没有实测 API，不下结论。
- 客观分奖励"布景与时序对齐"，时序不同的好成片会被低估，所以量规层不能撤；两层分歧时以逐帧对照图为准复核。
- n=1 条样本、单镜头简单主体。多镜头、人物、复杂动作未测。

## 产物清单（同目录）
ref.mp4（参考）｜ p0a/p0b/p0c.mp4（P0 三抽）｜ p1.mp4 ｜ p2.mp4 ｜ chart_scores.png（分数曲线）｜ montage_compare.png（REF/P0/P1/P2 对照）｜ sheet_*.png（各片 6 帧图）｜ sharingan-ref/、sharingan-p2/（实测层原始分析）
Skill 本体：./（SKILL.md＋scripts/score_pair.py＋templates/scorecard.md）

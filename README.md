# 20-giftwrap（礼品包装纸）

Giftwrap — 盒体展开近似面积（含重叠余量系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4900 |
| API | http://localhost:9900 |

## 主链

盒长宽高 → 包装纸面积 → 按卷宽折张（每张长 = 卷宽，张数 = ceil(用纸面积 ÷ 卷宽²)）→ 展开示意

`paper_m2 = 2(LW+LH+WH) × overlap` 的几何口径不变；折张只消费已舍入后的面积。

## 卷宽与快照口径

- 试算/新切张走**现行** `papers.roll_width`；纸张页保存卷宽当场生效，`roll_width ≤ 0` 拒绝（422）。同盒同卷，卷宽存得越小，张数不得下降。
- 已落库 run 的 `paper_id / roll_width / sheet_len / sheets` 钉住**写入时快照**（`calc_runs` 列，`result_json` 完整归档）；事后改卷宽不影响历史单据，列表 `GET /api/runs` 与详情 `GET /api/runs/{id}` 两路同源一致。
- 详情的 `recheck` 用落库时卷宽/系数 + 当前盒型尺寸再干算，与回看的张数互证。
- 算纸台当前选用纸由 `settings.selected_paper_id` 持久化，纸张页标记与算纸台下拉同源。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| PUT | `/api/papers/{id}` | 改卷宽/名称（`roll_width` 必须 > 0） |
| PUT | `/api/settings` | 设 `selected_paper_id`（纸须存在） |
| GET | `/api/runs/{id}` | run 详情 + `recheck` 互证 |

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。

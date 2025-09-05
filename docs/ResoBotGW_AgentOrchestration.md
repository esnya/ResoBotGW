# ResoBotGW — Agent分類と平行連携仕様 v0.2

本書は ResoBotGW プロジェクトの「Agent の種別」と「平行連携方法」に関する
**Contract‑First 概念設計**をまとめたものです。

---

## 1. 前提と目的
- **目的**: 自律性・娯楽性・環境認識・多人数適応・低レイテンシを並列エージェントの協調で実現する。
- **方式**: 各 Agent が **Intent** を入札し、**Arbiter** がリソース衝突を解消して同時コミット。
- **通信**: World ↔ AI は **DI (イベント)**／**DV (小状態)**。
- **平行の鍵**: `speech / locomotion / head / handsL / handsR / ui / sensors` のリソース。

---

## 2. Agent タクソノミ

| カテゴリ | Agent 名 | 主目的 | 代表 Intent | 要求リソース | 目標レイテンシ (P95) | 備考 |
|---|---|---|---|---|---|---|
| Reflex | DialogueReflex | テキスト/メンション即応 | `say{text}` | speech | 400–600ms | メンション優先 |
|        | GazeReflex     | 注視・顔向け | `look_at{slot}` | head | ≤150ms | 生きてる感 |
| Deliberative | Planner | 目標→手順 | `move_to/use/...` | 可変 | 800ms〜数秒 | HTN/GOAP/LLM |
| Motor/Skill | Navigation | 局所移動刻み | `move_to(step)` | locomotion | 250–350ms | Planner不在でも動作 |
|             | Manipulation | 把持・操作 | `grab/release/use` | handsL/R | 300–600ms | 手はL/R分離 |
|             | Emote/FX | エモート/演出 | `emote{type}` | ui | 200–400ms | 娯楽性補強 |
| Perception | SceneSense | 物体/ユーザ要約 | – | sensors | – | WM更新のみ |
|             | FocusSynth | 注視候補統合 | `look_at` | head | ≤200ms | 弱入札 |
| Social | TurnTaker | 公平順番制御 | `say` | speech | 400–700ms | Engagement重み |
| Activity | ActivityHost | 遊び進行管理 | `start/stop_activity` | 可変 | テンポ依存 | 中断安全 |
| Guardian | Safety/Policy | 否決/修正 | – | – | ≤50ms | 常時オン |
| Memory | Episodic/Semantic | 記録・検索 | – | – | – | 要約と参照のみ |

---

## 3. 平行実行モデル

### 3.1 リソース・トークン
- `speech`, `locomotion`, `head`, `handsL`, `handsR`, `ui`, `sensors`
- **Intent** は最低1つのリソースを宣言。
- **handsL/R** を分けて両手並行を許可。

### 3.2 互換マトリクス

| ←A\B→ | speech | locomotion | head | handsL | handsR | ui |
|---|---:|---:|---:|---:|---:|---:|
| speech | × | ○ | ○ | ○ | ○ | ○ |
| locomotion | ○ | × | ○ | △ | △ | ○ |
| head | ○ | ○ | × | ○ | ○ | ○ |
| handsL | ○ | △ | ○ | × | ○ | ○ |
| handsR | ○ | △ | ○ | ○ | × | ○ |
| ui | ○ | ○ | ○ | ○ | ○ | × |

- △: 歩行中の把持など制約付きで許容。

### 3.3 占有時間とプリエンプト
- Intentは `hold_ms` を持ち、その間リソースをロック。
- プリエンプト順序: reflex > safety > activity > planner。
- `say` と `look_at` は短占有で反応性を担保。

---

## 4. 連携プロトコル

- Proposal: `Intent{ kind, params, resources[], score }`
- Arbiter: tickごとに集約 → 整列 → 互換表に従い複数コミット。
- commitは `resobot.<bot>.commit`、結果は `resobot.<bot>.action.done`。

---

## 5. 協調パターン

- **低遅延反射**: `say + look_at + move_to(step)` の並列。
- **熟考行動**: Plannerのmove_to進行中にDialogueReflexのspeech割込み可。
- **把持併走**: locomotion中にhandsL grabを条件付き許容。Safetyで否決も。
- **多人数公平**: TurnTakerがEngagement重みでspeechを調整。

---

## 6. 多人数適応

- Engagement: `E = a*近接 + b*発話新鮮度 + c*メンション + d*視線交差`。
- Round-Robin with Salience: 高E優先、連続は抑制。
- `thread_id` をWMに保持し、対話文脈を維持。

---

## 7. 受け入れ条件

- **AC-1**: `say+look_at+move_to` が同tickで並列、各レイテンシ目標内。
- **AC-2**: 歩行中grabで速度降格、安全に成功。
- **AC-3**: 3–6人で同一ユーザ連続応答率 <60%。
- **AC-4**: 私有物操作はSafetyが必ず否決、理由をdetailに残す。

---

## 8. 次ステップ

1. Agent固定名・リソース固定・互換表を凍結。
2. Intent種別ごとの成功条件/副作用を整理。
3. Activity v0（pose_photo / scavenger）の設計票を策定。


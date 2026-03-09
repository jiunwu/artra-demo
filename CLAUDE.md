# ArTra Demo — Claude Code 開發指引

## 專案概述

基於 Cornelius et al. (2025) 的 ArTraDB 研究，用 2026 年的技術（LLM API + RAG）重新實作一個**輕量級 demo**，展示從分類學文獻中自動抽取「物種—特徵—數值」三元組的能力。

原論文使用 BioBERT + LUKE 的傳統 NLP pipeline，本 demo 改用 **Google Gemini API** 做 few-shot NER 與關係抽取，搭配純 HTML/JS 前端展示結果。

## 技術決策（已確認）

| 項目 | 選擇 | 原因 |
|------|------|------|
| LLM API | Google Gemini API | 使用者指定 |
| 前端 | 純 HTML/JS（單一檔案） | 最簡單直接，適合快速 demo |
| 後端 | Python (FastAPI) | 輕量、與 Gemini SDK 整合方便 |
| 範圍 | 輕量 LLM 抽取 demo | 專注 NER/RE，非完整 pipeline |

## 架構

```
artra-demo/
├── CLAUDE.md              # 本檔案：開發指引
├── PRD.md                 # 產品需求文件
├── reference/
│   ├── paper_context.md   # 原論文重點摘要（供 Claude Code 理解背景）
│   └── sample_texts.md    # 範例分類學文本（用於測試）
├── backend/
│   ├── main.py            # FastAPI 伺服器
│   ├── extractor.py       # Gemini API 呼叫邏輯（NER + RE）
│   ├── prompts.py         # Few-shot prompt 模板
│   ├── models.py          # Pydantic 資料模型
│   └── requirements.txt   # Python 依賴
├── frontend/
│   └── index.html         # 單一 HTML 檔案（含 CSS/JS）
└── data/
    ├── sample_output.json # 範例抽取結果（供前端開發用）
    └── trait_dictionary.json # 特徵詞典（精簡版，390 筆）
```

## 開發順序

請按以下順序實作：

### Phase 1：後端核心（extractor + API）
1. 讀取 `reference/paper_context.md` 理解領域背景
2. 實作 `backend/prompts.py` — 設計 few-shot prompt，包含 3-5 個標注範例
3. 實作 `backend/models.py` — 定義 Entity、Relationship、ExtractionResult 等 Pydantic model
4. 實作 `backend/extractor.py` — 呼叫 Gemini API，解析回傳的 JSON
5. 實作 `backend/main.py` — FastAPI 路由：POST /extract、GET /health
6. 測試：用 `reference/sample_texts.md` 中的文本測試抽取品質

### Phase 2：前端展示
7. 實作 `frontend/index.html` — 包含：
   - 文本輸入區（textarea）
   - 「抽取」按鈕，呼叫後端 API
   - 結果表格：顯示抽取出的三元組（物種、特徵、數值、信心分數）
   - 原文高亮：在輸入文本上用顏色標記辨識出的實體
   - 簡易統計：實體數量、關係數量

### Phase 3：優化與展示
8. 加入 loading 狀態與錯誤處理
9. 加入 2-3 個預設範例文本（一鍵載入）
10. 可選：加入簡易知識圖譜視覺化（用 D3.js 或 vis.js）

## Prompt 設計原則

Few-shot prompt 應包含以下結構：

```
你是一個生物多樣性文獻分析專家。從以下分類學文本中抽取：
1. **實體**：物種名（Arthropod）、特徵（Trait）、數值（Value）
2. **關係**：hasTrait（物種→特徵）、hasValue（特徵→數值）

輸出 JSON 格式：
{
  "entities": [
    {"text": "...", "type": "Arthropod|Trait|Value", "start": 0, "end": 10}
  ],
  "relationships": [
    {"subject": "...", "predicate": "hasTrait|hasValue", "object": "..."}
  ],
  "triplets": [
    {"arthropod": "...", "trait": "...", "value": "..."}
  ]
}

[範例 1]
輸入：...
輸出：...

[範例 2]
輸入：...
輸出：...
```

## 實體類型定義

- **Arthropod**：物種名、屬名、科名等分類學名稱（如 *Drosophila melanogaster*、Coleoptera）
- **Trait**：形態特徵、行為特徵、生態特徵（如 body length、habitat、diet、wing color）
- **Value**：特徵的具體數值或描述（如 5.6 mm、tropical forest、herbivorous、brownish-yellow）

## 關係類型定義

- **hasTrait**：物種 → 特徵（如 *Pachybrachis sassii* hasTrait body length）
- **hasValue**：特徵 → 數值（如 body length hasValue 5.6 mm）

## 環境變數

```
GEMINI_API_KEY=<使用者需自行設定>
```

## 注意事項

- Gemini API 回傳的 JSON 可能不完美，需要做 robust parsing（try/except + regex fallback）
- 前端的實體高亮用 `<span>` 標記，不同類型用不同顏色：Arthropod=綠色、Trait=藍色、Value=橘色
- CORS：FastAPI 需設定 allow_origins=["*"] 方便本地開發
- 所有 UI 文字用英文（因為處理的是英文論文），但註解可以用中文

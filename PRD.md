# ArTra Demo — 產品需求文件 (PRD)

## 1. 背景與動機

### 原始研究
Cornelius et al. (2025) 發表了一套從分類學文獻中自動抽取節肢動物特徵數據的 NLP pipeline，使用 BioBERT（NER）和 LUKE（RE），處理了 2,000 篇 PubMedCentral 文章，產生 65 萬個實體標注與 33 萬個關係標注。結果透過 ArTraDB (artradb.unil.ch) 公開。

### 原始研究的局限
- BioBERT/LUKE 是 2020 年前的模型架構，參數量小，泛化能力有限
- NER F1：Arthropod 0.78、Trait 0.55、Value 僅 0.37-0.44
- RE F1：最佳配置 macro-avg 0.65
- 實體標準化率低：物種 63%、特徵 12.7%
- 需要大量人工標注（兩位專家標注 25 篇文章）
- 僅處理英文文獻

### 本 Demo 目標
展示 2026 年 LLM 技術（Google Gemini）如何以 **few-shot learning** 方式，在**零微調**的情況下達到可比或更優的抽取效果，大幅降低部署門檻。

## 2. 核心功能

### F1：文本輸入
- 使用者可在 textarea 中貼入分類學文本（英文）
- 提供 3 個預設範例文本，一鍵載入
- 支援 100-5000 字元的文本長度

### F2：LLM 抽取
- 呼叫 Gemini API，使用 few-shot prompt 進行 NER + RE
- 輸出結構化 JSON：entities、relationships、triplets
- 顯示 API 回應時間

### F3：結果展示
- **三元組表格**：Arthropod | Trait | Value | Confidence
- **原文高亮**：在原始文本上標記辨識出的實體
  - Arthropod = 綠色底色
  - Trait = 藍色底色
  - Value = 橘色底色
- **統計摘要**：實體數量（按類型）、關係數量、三元組數量

### F4：預設範例
提供以下 3 個預設範例文本：

**範例 1 - 單一物種描述**（簡單）
> 單一甲蟲物種的形態描述，包含體長、顏色等特徵

**範例 2 - 多物種比較**（中等）
> 同一屬內多個物種的比較，包含棲息地和食性資訊

**範例 3 - 完整分類處理**（複雜）
> 一個完整的 taxonomic treatment，包含診斷、描述、分佈等多段落

## 3. 非功能需求

- **回應時間**：< 10 秒（Gemini API 回應 + 解析）
- **錯誤處理**：API 失敗時顯示友善錯誤訊息，不 crash
- **無需登入**：API key 在後端環境變數設定
- **單機部署**：`python main.py` 即可啟動，前端自動 serve

## 4. 技術架構

```
使用者 → [index.html] → POST /extract → [FastAPI] → [Gemini API]
                                              ↓
                                        解析 JSON 回傳
                                              ↓
                              [index.html] 渲染表格 + 高亮
```

### 後端 API

**POST /api/extract**
```json
// Request
{
  "text": "Pachybrachis sassii, body length 5.6 mm...",
  "model": "gemini-2.0-flash"  // 可選，預設 gemini-2.0-flash
}

// Response
{
  "entities": [
    {"text": "Pachybrachis sassii", "type": "Arthropod", "start": 0, "end": 19, "confidence": 0.95},
    {"text": "body length", "type": "Trait", "start": 21, "end": 32, "confidence": 0.92},
    {"text": "5.6 mm", "type": "Value", "start": 33, "end": 39, "confidence": 0.88}
  ],
  "relationships": [
    {"subject": "Pachybrachis sassii", "predicate": "hasTrait", "object": "body length"},
    {"subject": "body length", "predicate": "hasValue", "object": "5.6 mm"}
  ],
  "triplets": [
    {"arthropod": "Pachybrachis sassii", "trait": "body length", "value": "5.6 mm"}
  ],
  "processing_time_ms": 2340,
  "model_used": "gemini-2.0-flash"
}
```

**GET /api/health**
```json
{"status": "ok", "gemini_available": true}
```

**GET /api/examples**
```json
[
  {"id": 1, "title": "Single species description", "text": "..."},
  {"id": 2, "title": "Multi-species comparison", "text": "..."},
  {"id": 3, "title": "Full taxonomic treatment", "text": "..."}
]
```

## 5. 前端 UI 規格

### 佈局
```
┌─────────────────────────────────────────────┐
│  ArTra Demo — Arthropod Trait Extractor     │
│  Powered by Gemini API (2026)               │
├─────────────────────────────────────────────┤
│                                             │
│  [Example 1] [Example 2] [Example 3]       │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ Paste taxonomic text here...        │    │
│  │                                     │    │
│  │                                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  [🔍 Extract Traits]        ⏱ 2.3s         │
│                                             │
├─────────────────────────────────────────────┤
│  Annotated Text                             │
│  ┌─────────────────────────────────────┐    │
│  │ [Pachybrachis sassii] has a         │    │
│  │ [body length] of [5.6 mm]...       │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Extracted Triplets (3 found)               │
│  ┌──────────┬────────────┬──────────┬───┐   │
│  │Arthropod │ Trait      │ Value    │ C │   │
│  ├──────────┼────────────┼──────────┼───┤   │
│  │P. sassii │body length │ 5.6 mm  │.95│   │
│  │P. sassii │color       │ brown   │.88│   │
│  └──────────┴────────────┴──────────┴───┘   │
│                                             │
│  Stats: 5 entities │ 4 relations │ 3 trips  │
└─────────────────────────────────────────────┘
```

### 配色
- Arthropod 實體：`#d4edda`（淺綠）邊框 `#28a745`
- Trait 實體：`#d1ecf1`（淺藍）邊框 `#17a2b8`
- Value 實體：`#fff3cd`（淺橘）邊框 `#ffc107`
- 主色調：`#1a3c6e`（深藍）
- 背景：`#f8f9fa`

## 6. 與原論文的比較展示（可選）

在結果區下方加一個小 section：

| 指標 | 原論文 (BioBERT+LUKE) | 本 Demo (Gemini) |
|------|---------------------|-----------------|
| 模型大小 | ~110M + ~340M params | Cloud API |
| 訓練數據 | 25 篇手動標注 | 0（few-shot） |
| NER 方法 | Fine-tuned BioBERT | Few-shot Gemini |
| RE 方法 | Fine-tuned LUKE | Few-shot Gemini |
| 部署需求 | GPU + 訓練 pipeline | API key only |

## 7. 成功指標

- Demo 能在 10 秒內回傳抽取結果
- 對預設 3 個範例文本，能正確抽取 >80% 的三元組
- 前端能正確高亮所有辨識出的實體
- 單一命令 `python backend/main.py` 啟動，前端可在 localhost 訪問

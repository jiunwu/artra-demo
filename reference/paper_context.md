# 原論文背景知識（供 LLM 開發參考）

## 論文資訊
- **標題**: From literature to biodiversity data: mining arthropod organismal and ecological traits with machine learning
- **作者**: Cornelius, Detering, Lithgow-Serrano, Agosti, Rinaldi, Waterhouse
- **年份**: 2025
- **DOI**: 10.1101/2025.02.18.638830

## 核心任務

從分類學文獻中抽取三種實體和兩種關係：

### 實體類型 (Named Entities)
1. **Arthropod** — 節肢動物的分類學名稱
   - 物種名：*Pachybrachis sassii*, *Drosophila melanogaster*
   - 屬名：*Tipula*, *Micrencaustes*
   - 科名：Chrysomelidae, Celyphidae
   - 目名：Coleoptera, Hymenoptera, Diptera

2. **Trait** — 生物特徵
   - 形態特徵：body length, wing venation, antenna segments, leg color
   - 生態特徵：habitat, elevation range, host plant
   - 行為特徵：feeding ecology, mating behavior
   - 分佈：distribution, geographic range

3. **Value** — 特徵的具體數值或描述
   - 數值型：5.6 mm, 2000-3500 m, 12 segments
   - 描述型：brownish-yellow, tropical forest, herbivorous
   - 地理型：Mediterranean, China, Brazil

### 關係類型 (Relationships)
1. **hasTrait**: Arthropod → Trait
   - *Pachybrachis sassii* → body length
   - Hymenoptera → feeding ecology

2. **hasValue**: Trait → Value
   - body length → 5.6 mm
   - habitat → tropical forest

### 三元組 (Triplets)
完整的知識單元：Arthropod → Trait → Value
- *Pachybrachis sassii* → body length → 5.6 mm
- *Tipula* → distribution → Mediterranean

## 原論文的技術 Pipeline

```
PubMedCentral 文章 (2,000 篇)
        ↓
    文本前處理
        ↓
NER (BioBERT, fine-tuned)  → 實體識別
        ↓
RE (LUKE, fine-tuned)      → 關係抽取
        ↓
OGER                       → 實體標準化（對應到詞典）
        ↓
ArTraDB                    → Web 展示
```

## 原論文的效能基線

### NER (命名實體識別)
| Entity Type | F1 (CoNLL) | F1 (Strict) | Precision | Recall |
|-------------|-----------|-------------|-----------|--------|
| Arthropod   | 0.74      | 0.78        | 0.78      | 0.78   |
| Trait        | 0.55      | 0.56        | 0.55      | 0.57   |
| Value        | 0.37      | 0.44        | 0.43      | 0.44   |
| Macro avg    | 0.56      | 0.59        | 0.63      | 0.57   |

### RE (關係抽取) — 最佳配置 NCB+Tag
| Relation Type | F1   | Precision | Recall |
|---------------|------|-----------|--------|
| hasTrait      | 0.55 | 0.55      | 0.55   |
| hasValue      | 0.64 | 0.60      | 0.69   |
| none          | 0.77 | 0.83      | 0.72   |
| Macro avg     | 0.65 | 0.66      | 0.69   |

## 特徵詞典分類

原論文的 390 個特徵分為三大類：
- **Feeding ecology** (食性生態): 81 項 — herbivore, predator, parasite, detritivore...
- **Habitat** (棲息地): 184 項 — forest, grassland, aquatic, cave, urban...
- **Morphology** (形態學): 125 項 — body length, wing shape, antenna type, color pattern...

## 標注複雜度

兩位專家標注的 Cohen's Kappa 一致性：
- 實體標注：0.35 ~ 0.8（變異很大）
- 關係標注：普遍低於實體標注
- 說明此任務即使對人類專家也具有挑戰性

## 本 Demo 的改進方向

1. **用 Gemini few-shot 替代 fine-tuned BioBERT/LUKE** → 零訓練成本
2. **單一 API 呼叫同時完成 NER + RE** → 簡化 pipeline
3. **JSON 結構化輸出** → 不需要 IOB2 格式轉換
4. **多語言潛力** → Gemini 原生支援中文等語言

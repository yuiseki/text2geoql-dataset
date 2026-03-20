# ADR-009: 自然言語概念と OSM タグの意味的グルーピング

## ステータス
Accepted

## コンテキスト

OSM のタグ体系と自然言語の概念には、1:1 で対応しない箇所が多数存在する。主に 2 種類の乖離がある。

### 問題 1: OSM タグ名前空間の二重化（`amenity=` vs `healthcare=`）

OSM では `amenity=hospital` 等の旧来タグと、より体系的な `healthcare=` 名前空間が並存している。包括的な検索には両方をカバーする union クエリが必要。

| OSM タグ | 件数 | 意味 |
|----------|------|------|
| `amenity=hospital` | 215,937 | 入院対応の大病院（旧タグ） |
| `healthcare=hospital` | 126,770 | 同上（新タグ） |
| `amenity=clinic` | 210,029 | 外来クリニック（旧タグ） |
| `healthcare=clinic` | 137,073 | 同上（新タグ） |
| `amenity=doctors` | 198,691 | 個人医院・内科等（旧タグ） |
| `healthcare=doctor` | 142,932 | 同上（新タグ） |
| `amenity=pharmacy` | 427,911 | 薬局（旧タグ） |
| `healthcare=pharmacy` | 307,419 | 同上（新タグ） |

### 問題 2: 自然言語の概念スコープが言語・文化によって異なる

「病院」という概念を例にとると、対応する OSM タグは言語・文化によって異なる：

| 言語・文化 | 「病院に行く」の意味するスコープ | 対応 OSM タグ |
|-----------|-------------------------------|--------------|
| 日本語 | `hospital` + `clinic` + `doctors` をまとめて「病院」と呼ぶ | 3 タイプ全て |
| 英語 | "hospital" は入院施設を指し、"clinic" "doctor's office" は別概念 | `hospital` のみ |
| 韓国語 | 「병원」は日本語の「病院」に近く広義 | おそらく 3 タイプ |
| フランス語 | "hôpital" と "cabinet médical" は明確に区別される | `hospital` のみ |

これは翻訳・文化の問題であり、**OSM タグの技術的な問題ではなく、人間の概念の問題**である。同じ TRIDENT 命令 `AreaWithConcern: Shinjuku, Tokyo, Japan; 病院` を英語話者と日本語話者に見せたとき、期待する OverpassQL が異なりうる。

さらに複雑なのは、**日本のデータセットでは日本語の感覚が正解**だが、**ソウルのデータセットを英語で書くとき**（`AreaWithConcern: Gangnam-gu, Seoul, South Korea; Hospitals`）はどちらの感覚で書くべきかが曖昧になる点である。

### 問題 3: 粒度の選択が恣意的になる

- "Hospitals and Clinics" だと `doctors` が抜ける
- "Medical Facilities" にまとめると今度は広すぎる（歯科・薬局まで含むか？）
- どこで線を引くかに正解がない

## 決定

この問題を**完全には解決せず**、以下の方針で現実的に対処する。

### 方針 1: `amenity=` と `healthcare=` の二重化は常に両方カバーする

これは文化によらない純粋な技術的問題であり、解決できる。すべての医療・薬局関連クエリでは `amenity=X` と `healthcare=X` の両方を union に含める。

```overpassql
/* 病院の例 */
(
  nwr["amenity"="hospital"](area.target);
  nwr["healthcare"="hospital"](area.target);
);
out geom;
```

### 方針 2: 概念スコープは「広め」を基本としつつ、段階的な粒度を用意する

概念の境界が文化依存で曖昧なため、**より広いスコープを持つ複合エントリを基本とし**、必要に応じて精密エントリも残す。

具体的には「医療施設」系を以下の 3 段階に整理する：

| TRIDENT 関心事 | カバーする OSM タグ | 想定する自然言語 |
|--------------|-------------------|----------------|
| `Hospitals` | `amenity=hospital` + `healthcare=hospital` | "大病院"、"入院できる病院" |
| `Clinics and Doctors` | `amenity=clinic` + `healthcare=clinic` + `amenity=doctors` + `healthcare=doctor` | "クリニック"、"診療所" |
| `Medical Facilities` | 上記すべての union | "病院"（日本語的な広義） |
| `Pharmacies` | `amenity=pharmacy` + `healthcare=pharmacy` | "薬局" |

### 方針 3: 多言語的な曖昧さをデータセットに意図的に含める

TRIDENT の関心事名は英語で書かれているが、「どの英語表現がどの OSM タグスコープに対応するか」を Few-Shot 例の中で複数のパターンとして学習させる。

- `Hospitals` の例 → `amenity=hospital` のみのクエリ
- `Medical Facilities` の例 → 広義の union クエリ
- 両方が Few-Shot プールにあることで、LLM はコンテキストに応じて使い分けを学習する

### 方針 4: 言語・文化依存の問題は将来の課題として ADR に記録する

TRIDENT を多言語化（`AreaWithConcern: 新宿, 東京, 日本; 病院`）する場合、概念スコープのマッピングを言語別に定義する必要が生じる。これは ADR-010 以降の課題とする。

## 結果

**ポジティブ：**
- `amenity=` / `healthcare=` の二重化問題は確実に解決できる
- 広義・狭義の両方の例をデータセットに含めることで、LLM が状況に応じたクエリを生成できるようになる
- 曖昧さを隠蔽せず ADR に明記することで、将来のデータセット拡張者が同じ判断を繰り返さずに済む

**ネガティブ：**
- 「Medical Facilities」の概念スコープはデータセット作成者の文化的背景に依存し、完全に中立ではない
- 多言語対応を本格的にやるには TRIDENT フォーマット自体の拡張が必要（未解決）
- 広義の複合エントリは union クエリの行数が増え、MAX_QUERY_LINES=20 に抵触する可能性がある

## 補足

### 同様の文化依存問題が起きうる他の概念

| 概念 | 日本語的スコープ | 英語的スコープ |
|------|----------------|---------------|
| 学校 | 小学校〜大学まで「学校」 | school / college / university は明確に別 |
| お店 | 幅広い | shop の種類は細かく区別 |
| 神社・寺 | 神社と寺は別 | 欧米では両方 "temple/shrine" |
| コンビニ | 「コンビニ」は日本固有概念 | "convenience store" は英語にもあるが文化的重みが異なる |

### good_concerns.yaml への反映

```yaml
# 精密エントリ（特定タグ）
Hospitals: data/concerns/amenity/hospital              # amenity= + healthcare= の hospital
Clinics and Doctors: data/concerns/medical/clinic_and_doctor  # clinic + doctors の union
Pharmacies: data/concerns/medical/pharmacy             # amenity= + healthcare= の pharmacy

# 複合エントリ（日本語「病院」相当の広義）
Medical Facilities: data/concerns/medical/all          # hospital + clinic + doctors の union
```

関連 ADR:
- ADR-001: TRIDENT 中間表現（関心事名の設計）
- ADR-003: LLM Few-Shot プロンプティング（union 構文例の追加）
- ADR-008: Taginfo（`healthcare=` 名前空間の実態把握）

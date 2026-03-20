# Architecture Decision Records

このディレクトリは text2geoql-dataset プロジェクトの Architecture Decision Records (ADR) を管理します。

ADR は「なぜそのような設計を選んだか」という意思決定の記録です。実装の真として現在動いているコードベースと同期を保ちます。

## 一覧

| No. | タイトル | ステータス |
|-----|----------|----------|
| [ADR-001](ADR-001-trident-intermediate-representation.md) | TRIDENT 中間表現の採用 | Accepted |
| [ADR-002](ADR-002-self-hosted-overpass-api-grounding.md) | セルフホスト Overpass API によるグラウンディング | Accepted |
| [ADR-003](ADR-003-llm-few-shot-overpassql-generation.md) | LLM + Few-Shot プロンプティングによる OverpassQL 生成 | Accepted |
| [ADR-004](ADR-004-hierarchical-file-based-dataset-storage.md) | OSM タグスキーマに準拠した階層ファイルベースのデータセット構造 | Accepted |
| [ADR-005](ADR-005-provenance-and-failure-metadata.md) | 生成プロベナンスと失敗メタデータの記録 | Accepted |
| [ADR-006](ADR-006-multi-model-benchmark-framework.md) | マルチモデルベンチマーク基盤 | Accepted |
| [ADR-007](ADR-007-nominatim-area-grounding.md) | Nominatim による地名グラウンディング | Proposed |
| [ADR-008](ADR-008-taginfo-osm-tag-knowledge.md) | Taginfo API による OSM タグ知識のグラウンディング | Proposed |
| [ADR-009](ADR-009-semantic-tag-grouping.md) | 自然言語概念と OSM タグの意味的グルーピング | Accepted |

## ADR テンプレート

```markdown
# ADR-NNN: タイトル

## ステータス
Proposed / Accepted / Deprecated / Superseded by ADR-NNN

## コンテキスト
（なぜこの意思決定が必要になったか）

## 決定
（何を選んだか）

## 根拠
（なぜそれを選んだか）

## 結果
（この決定によって何が起きるか：ポジティブ・ネガティブ両面）

## 補足
（実装上の注意点・参考リンクなど）
```

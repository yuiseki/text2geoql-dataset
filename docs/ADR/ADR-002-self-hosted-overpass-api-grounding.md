# ADR-002: セルフホスト Overpass API によるグラウンディング

## ステータス
Accepted

## コンテキスト

LLM が生成した OverpassQL クエリが「意味的に正しいか」を検証する方法が必要だった。候補として以下を検討した：

1. **静的なクエリ構文チェックのみ**: Overpass QL の文法が正しいかだけを検証
2. **公開 Overpass API への問い合わせ**: `https://overpass-api.de/` 等のパブリックエンドポイント
3. **セルフホスト Overpass API への問い合わせ**: 自前のインスタンスを用意する

構文が正しいだけでは不十分である。たとえば `[amenity=cafe]` というタグが `nwr` に付与されていても、指定したエリアにカフェが実際に存在しなければクエリは意味をなさない。**現実の OSM データによる検証（グラウンディング）が不可欠**だった。

公開 API は高負荷なデータセット生成ワークロードには向かない（レートリミット、タイムアウト、利用規約の制約）。

## 決定

**自前の Overpass API インスタンス（`https://overpass.yuiseki.net/api/interpreter`）を用意し、すべての検証クエリをそこに投げる。**

検証基準：

```python
# 成功条件: Overpass API から 1 件以上の要素が返ること
elements = fetch_elements(overpassql)
if len(elements) > 0:
    # 保存
else:
    # FailureMeta(reason="zero_results") を記録
```

クエリのタイムアウトは `[timeout:30]`（30秒）に統一する。これを超えると API が 504 を返すため、プロンプトおよびすべてのデータファイルに `[timeout:30]` を強制する。

実装は `src/overpass.py` に集約し、エンドポイントを引数で注入できる設計にしてテストを容易にする。

## 根拠

- **現実の OSM データによる正確性保証**: LLM が生成したタグ（`amenity=cafe`、`tourism=hotel` 等）が実際の OSM データに存在することを確認できる
- **レートリミット回避**: セルフホストなので大量のリクエストを気兼ねなく投げられる
- **再現性**: 公開 API はデータ更新やメンテナンスで挙動が変わることがあるが、セルフホストなら同一データでの比較が可能
- **エンドポイント注入**: `fetch_elements(query, endpoint=...)` でテスト時にモックや別インスタンスを使える

## 結果

**ポジティブ：**
- データセット内の全クエリが「現実に存在する場所・施設を返す」ことが保証される
- 高スループットでの並列生成が可能（レートリミットなし）
- `zero_results` を明示的な失敗として記録することで、データセットの品質が担保される
- ネットワーク不要のテスト（`overpass.py` のモック）と本番の両方をサポート

**ネガティブ：**
- セルフホスト Overpass インスタンスの維持コスト（ハードウェア、OSM データ更新）が必要
- OSM データは時間とともに変化するため、過去に生成したクエリが現在は `zero_results` になる可能性がある（データセットのドリフト）
- `timeout:30` は複雑なクエリでは短い場合があり、一部の広域クエリが失敗する可能性

## 補足

実装: `src/overpass.py`
テスト: `tests/test_overpass.py`（httpx モック使用）

**重要な過去の問題**: 当初プロンプトおよびデータファイルに `[timeout:30000]`（ミリ秒？）を誤記していた。Overpass API の `timeout` は秒単位であり、`timeout:30000` は 30000 秒 = 約 8 時間という異常値になる。Overpass プロキシが 504 を返していたのはこのため。2026-03-20 にプロンプトおよび全 1582 データファイルを `[timeout:30]` に修正済み。

```python
# src/overpass.py
DEFAULT_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"

def fetch_elements(query: str, endpoint: str = DEFAULT_ENDPOINT) -> list[dict]:
    response = httpx.post(endpoint, data={"data": query}, timeout=60)
    return response.json().get("elements", [])
```

# RegexPad 追加資材・手動削除用一覧

このファイルはEXEの`_internal`に同梱され、初回起動時と追加資材の準備後に実際の保存先で更新されます。
控えはアプリ横の`install_records/DELET_ITEMS_LIST.md`、構造化した記録は`install_records/deletion_inventory.json`です。

- 削除前にRegexPadとWordPressを終了し、この一覧を必要に応じて別の場所へ保存してください。
- 「アプリ内」や「追加処理の記録」は所在の説明です。この一覧だけを根拠に自動削除はしません。
- アプリ外・共有環境・所有未確認の項目は、その場所を他のソフトも使用していないか確認してください。
- 設定ファイルはパスだけを記録し、内容・パスワード・環境変数全体は収集しません。
- WordPressがメモリー内で展開したコア・プラグインは、プロセス終了時に解放されます。ホスト側のZIP・実行部品・キャッシュをこの一覧に記録します。

<!-- REGEXPAD-INVENTORY-BEGIN -->
初回記録: 2026-10-25T14:52:56+09:00  
最終更新: 2026-10-25T14:52:56+09:00  
配置先: `D:\PC\Python\regex_pad_project`

## 資材・設定ファイルの保存先

| 区分 | パス | 現在 | 所在・注意 |
|---|---|---|---|
| WordPressプレビュー用資材 | `D:\PC\Python\regex_pad_project\_internal\resources\wordpress_preview` | なし／未作成・削除済み | アプリ専用領域（同梱分または起動後に作成） |
| WordPress同梱資材 | `D:\PC\Python\regex_pad_project\_internal\runtime\wordpress-preview` | なし／未作成・削除済み | アプリ専用領域（同梱分または起動後に作成） |
| アプリ用キャッシュ | `D:\PC\Python\regex_pad_project\cache` | あり | アプリ専用領域（同梱分または起動後に作成） |
| 設定ファイル | `D:\PC\Python\regex_pad_project\config.json` | あり | 検出したパスのみ（内容は未収集、所有は個別確認） |
| 一時データ | `D:\PC\Python\regex_pad_project\data\temp` | あり | アプリ専用領域（同梱分または起動後に作成） |
| ログ | `D:\PC\Python\regex_pad_project\logs` | あり | アプリ専用領域（同梱分または起動後に作成） |
| Python追加モジュール | `D:\PC\Python\regex_pad_project\modules\site-packages` | あり | アプリ専用領域（同梱分または起動後に作成） |
| Python取得ファイル | `D:\PC\Python\regex_pad_project\modules\wheels` | あり | アプリ専用領域（同梱分または起動後に作成） |
| Python実行環境 | `D:\PC\Python\regex_pad_project\runtime\venv` | あり | アプリ専用領域（同梱分または起動後に作成） |
| WordPress追加処理先 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview` | あり | 実際に指定された準備先 |
| 使用するNode | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node\node-v24.22.1-win-x64\node.exe` | あり | 選択された実行ファイル（外部の既存Nodeは削除しない） |
| INI設定（未作成の場合は使用なし） | `D:\PC\Python\regex_pad_project\settings.ini` | なし／未作成・削除済み | アプリ専用領域（同梱分または起動後に作成） |
| 旧アプリ設定 | `D:\PC\Python\regex_pad_project\settings.json` | なし／未作成・削除済み | アプリ専用領域（同梱分または起動後に作成） |
| WordPress初期化・書き出し | `D:\PC\Python\regex_pad_project\Temp\WordPressPreview` | あり | アプリ専用領域（同梱分または起動後に作成） |

## Python追加モジュール

| 名前 | バージョン | 保存先 | 現在 |
|---|---|---|---|
| 該当記録なし | — | — | — |

## WordPress実行部品（npm）

| 名前 | バージョン | 保存先 | 現在 |
|---|---|---|---|
| @php-wasm/logger | 3.1.60 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\@php-wasm\logger` | あり |
| @php-wasm/node-8-3 | 3.1.60 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\@php-wasm\node-8-3` | あり |
| @php-wasm/progress | 3.1.60 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\@php-wasm\progress` | あり |
| @php-wasm/stream-compression | 3.1.60 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\@php-wasm\stream-compression` | あり |
| @php-wasm/universal | 3.1.60 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\@php-wasm\universal` | あり |
| @php-wasm/util | 3.1.60 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\@php-wasm\util` | あり |
| @wp-playground/common | 3.1.60 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\@wp-playground\common` | あり |
| @wp-playground/wordpress | 3.1.60 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\@wp-playground\wordpress` | あり |
| ini | 4.1.2 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\ini` | あり |
| wasm-feature-detect | 1.8.0 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\wasm-feature-detect` | あり |
| zstddec | 0.2.0 | `D:\PC\Python\regex_pad_project\runtime\wordpress-preview\node_modules\zstddec` | あり |

## プロセス内の環境変数

| 名前 | 値・参照先 | 適用範囲 |
|---|---|---|

## 永続的な環境変数・レジストリ

本アプリによる作成なし。削除する永続環境変数・レジストリキーはありません。
既存の共有Node・Python・PATH設定を削除しないでください。INI等は内容を読まず、上の保存先一覧にパスだけを記録します。

---

# (警告)共有する可能性が高いファイル

## 以下のファイル・フォルダなどは、他のソフトから共有されている可能性が有ります。

他のソフトでの利用と所有を確認してから、削除の要否を判断してください。自動削除対象にはしません。既存の環境変数の参照先もこちらに記載します。

| 区分 | Path | 現在 | 参照元・注意 |
|---|---|---|---|
| 該当記録なし | — | — | — |
<!-- REGEXPAD-INVENTORY-END -->

## 手動メモ

この欄など、自動生成範囲の外に記入した内容は更新時にも保持します。

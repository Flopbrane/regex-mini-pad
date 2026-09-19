regex-pad 配布フォルダ用 README
==============================

ソフト名:
regex-pad

目的:
正規表現の検索・置換を扱いやすくする、Windows向けの軽量テキストエディタです。

起動方法:
このフォルダ内の regex-pad.exe を実行してください。

ワンフォルダ運用方針:
設定、キャッシュ、ログ、一時ファイル、インストール記録は、可能な限りこのフォルダ内へ保存します。
Pythonモジュールは module_installer.py により runtime/venv へ入れる方針です。

使用する可能性がある外部モジュール:
requirements_dev.txt に記載されたPythonモジュールを使用します。
このソフト単体ではAIモデルや学習済みデータの同梱を前提にしていません。

削除時に使うソフト:
module_cleaner.exe

削除順序:
1. regex-pad.exe を終了してください。
2. module_cleaner.exe --scan を実行し、現在状態を確認してください。
3. module_cleaner.exe --dry-run を実行し、削除候補を確認してください。
4. 問題がなければ module_cleaner.exe --clean を実行してください。
5. 最後に regex-pad フォルダを手動で削除してください。

削除してよいもの:
- install_records/install_diff.json に記録された、このアプリが追加したファイル
- regex-pad フォルダ内の cache、runtime、logs、data など

削除してはいけないもの:
- このフォルダ外にあるPython本体
- このフォルダ外にある既存venv
- ユーザーが別用途で使っているsite-packages
- 記録上、このアプリが作成したと確認できないファイル

ライセンス:
LICENSE.txt を確認してください。
外部モジュールのライセンスは、requirements_dev.txt および各配布元の条件を確認してください。

免責事項:
このソフトの使用、削除、編集結果によって発生した損害について、作者は責任を負いません。
重要なファイルは事前にバックアップしてください。

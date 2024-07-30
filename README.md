# Digital Imaging Cloud

Digital Imaging Cloudは、FTPサーバーとして機能し、受信した画像ファイルをGoogleフォトに自動的にアップロードするPythonアプリケーションです。
SONY αシリーズデジタルカメラのFTP機能を用いて、PCやスマートフォンレスでGoogleフォトへ写真をアップロードすることを想定しています。

## 機能

- FTPサーバーとしての機能
- 受信したJPEGファイルの自動検出とGoogleフォトへの自動アップロード
- 日本語を含むファイル名のサポート
- アップロード済みファイルの重複アップロード防止
- アップロード成功後のローカルファイル自動削除
- 詳細なログ機能
- マルチスレッド対応のファイル処理

## 前提条件

- Python 3.9以上
- rye（Pythonパッケージマネージャー）
- Google Cloudプロジェクトとcredentials.json
- SQLite3（通常Pythonに標準搭載）

## セットアップ

1. リポジトリをクローンします：
   ```
   git clone https://github.com/okakennn/DigitalImagingCloud.git
   cd digital-imaging-cloud
   ```

2. ryeを使用して依存関係をインストールします：
   ```
   rye sync
   ```

3. Google Cloud Consoleで新しいプロジェクトを作成し、Photos Library APIを有効にします。

4. OAuth 2.0クライアントIDを作成し、credentials.jsonとしてダウンロードします。

5. credentials.jsonファイルをプロジェクトのルートディレクトリに配置します。

## 使用方法

1. アプリケーションを起動します：
   ```
   rye run python src/digitalimagingcloud/main.py
   ```

2. 初回実行時、Google認証のためのURLが表示されます。URLをブラウザで開き、認証を完了してください。

3. FTPクライアントを使用して、設定されたFTPサーバー（デフォルトでポート2121）に接続します。

4. JPEGファイルをアップロードすると、自動的にGoogleフォトにアップロードされます。アップロード成功後、ローカルファイルは自動的に削除されます。

## 設定

- FTPサーバーのポートやアップロードディレクトリは`src/digitalimagingcloud/main.py`で設定できます。
- ログレベルは`src/digitalimagingcloud/utils/logging_config.py`で調整できます。
- アップロード履歴データベースのパスは`src/digitalimagingcloud/upload_manager.py`の`UploadManager`クラスで設定できます。

## 注意事項

- このアプリケーションはローカルネットワーク内での使用を想定しています。
- アップロード履歴はSQLiteデータベースに保存されます。リセットする場合、upload_history.dbを削除し再起動してください。

## トラブルシューティング

- ログファイル（digital_imaging_cloud.log）を確認して、詳細なエラー情報を得ることができます。
- 認証に問題がある場合は、credentials.jsonが正しく配置されているか確認してください。
- アップロードの重複や失敗が発生した場合、upload_history.dbファイルを確認してください。

## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

# Version: bamboo-analyze-v1

# 概要

- 草コイン銘柄の上昇率の統計をとり、解析する

# 前準備

- 以下の URL を参考に pip をインストール
  - 'https://docs.aws.amazon.com/ja_jp/cloud9/latest/user-guide/sample-python.html'
- `sudo yum update`
- `pip3 install python-binance --user` を実行

# 各種設定

- settings.json

  - `access_key`と`secret_key`を設定

    - binance の API キーを発行した時にそれぞれ控えておく

  - price_rise_rate_list を設定

    - 検出後の価格上昇率のラダー

  - detection_price_rise_rate_list を設定

    - 上昇率検出のラダー

  - losscut_price_rate を設定

    - 損切りする価格下落率の閾値

  - price_check_interval を設定

    - 価格チェックの頻度(秒)

  - symbol を設定

    - 統計対象の建て銘柄を設定
    - 例: `"USDT"`

  - chatwork への通知設定

    - notify を設定

      - 通知するかしないか

    - chatwork_api_token を設定
    - chatwork_room_id を設定

- UTC+9 にサーバー時間を設定

  - 'https://hx2.jp/archives/4248'

- blacklist.json でリスト内に検知対象外の銘柄を設定
  - 例: `["BTC", "ETH"]`

# プログラム実行コマンド(下のターミナルに入力し、Enter キーで実行)

`sudo python3.7 myapp.py`

# プログラムの中断(ターミナルで Ctrl + C)

# プロセスをキルするコマンド(下のターミナルに入力し、Enter キーで実行)

`sudo kill -9 $(ps aux | grep '[p]ython3.7 myapp.py' | awk '{print $2}')`

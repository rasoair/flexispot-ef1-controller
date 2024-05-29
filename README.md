# flexispot EF1 Controller

**このリポジトリに含まれるコードは、LoctekMotion_IoT[^1]リポジトリをもとに書かれたものであり、flexispot EF-1をCLI・GUI操作するためのツールとして新たに作成されたものです。**

## 概要
- 

## 操作の方法


### APIエンドポイント

## 使用している技術およびライブラリ等
- Hardware
  - Raspberry pi 4B
  - RJ45ケーブル
- Software & libraries
  - Python3.11.2
  - ライブラリについては、requirements.txtを参照


## トラブルシューティング

### コントローラと通信するための権限がない場合
"ttyS0"に関するPermissionエラーが発生した場合は以下を実行して権限を付与
```
$ chmod a+rw /dev/ttyS0
```

[^1]: https://github.com/iMicknl/LoctekMotion_IoT

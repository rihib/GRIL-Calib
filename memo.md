# Memo

## クイックスタート

### 事前準備

```bash
git clone https://github.com/Taeyoung96/GRIL-Calib.git
cd GRIL-Calib

# m2dgr/gate01 データセットのダウンロード
mkdir -p data/m2dgr/gate01
cd data/m2dgr/gate01
# https://github.com/SJTU-ViSYS/M2DGR#outdoors のダウンロードリンクの末尾に `&download=1` を付与
wget -O gate_01.bag "https://sjtueducn-my.sharepoint.com/:u:/g/personal/594666_sjtu_edu_cn/ET3mU1rvdTpEl8VYvC25q7YB5pmPQlwru0jBbQ9iu0oAMA?e=LrKUpJ&download=1"

# イメージのビルド
cd ../../../docker
docker build -t gril-calib .
chmod -R 777 container_run.sh
```

### 実行

```bash
# コンテナの起動
./container_run.sh gril-calib-container gril-calib:latest

# コンテナ内
catkin_make
source devel/setup.bash
roslaunch gril_calib m2dgr_gate01.launch  # launch/*/*.launch
```

```bash
# 別ターミナル
cd docker
docker exec -it gril-calib-container bash

# コンテナ内
source /opt/ros/noetic/setup.bash
rosbag play /root/bags/m2dgr/gate01/gate_01.bag
```

### 結果

```bash
# result/GRIL_Calib_result.txt
LiDAR-IMU calibration result:
Rotation LiDAR to IMU (degree)     = -0.129590  0.268340  0.579889
Translation LiDAR to IMU (meter)   = 0.214359 0.051815 0.178496
Time Lag IMU to LiDAR (second)     = -0.108240
Bias of Gyroscope  (rad/s)         =  0.001313 -0.000617  0.003870
Bias of Accelerometer (meters/s^2) = -0.010147  0.009875 -0.009976

Homogeneous Transformation Matrix from LiDAR frmae L to IMU frame I: 
 0.999938 -0.010131  0.004660  0.214359
 0.010120  0.999946  0.002309  0.051815
-0.004683 -0.002262  0.999986  0.178496
 0.000000  0.000000  0.000000  1.000000
```

### GT との比較

#### GT の所在

M2DGR gate-01 の IMU-LiDAR 外部パラメータ GT は、データセット内の複数ファイルに記載されている。GRIL-Calib が使うメイン IMU は Handsfree A9。

M2DGR 公式の [`calibration_results.txt`](https://github.com/SJTU-ViSYS/M2DGR/blob/main/calibration_results.txt) の末尾に **Handsfree IMU**（= Handsfree A9）の外部パラメータが記載されている。`data` は OpenCV 形式の 3×4 外部パラメータ行列 `[R | t]` を平坦化したもので、各行が「回転 3 成分 | 並進 1 成分」になっている。回転 R は左 3×3 ブロック（= 単位行列）、並進 t は右端列 `[-0.27255, 0.00053, -0.17954]`。

```text
%% Handsfree IMU
% Extrinsic [to LIDAR]                ← 3×4 の [R | t]
data: [1., 0., 0., -0.27255,         # R 行0 = (1,0,0) | tx = -0.27255
       0., 1, 0., 0.00053,           # R 行1 = (0,1,0) | ty =  0.00053
       0., 0., 1., -0.17954]         # R 行2 = (0,0,1) | tz = -0.17954
# 左 3×3 = [[1,0,0],[0,1,0],[0,0,1]] = 単位行列（回転 GT = 0°）/ 右端列 = 並進
```

検算: GRIL-Calib は LiDAR → IMU 表記を使う。回転が単位行列なので、上記 `[to LIDAR]` の並進 `[-0.27255, 0.00053, -0.17954]`（IMU → LiDAR） を符号反転して GT（LiDAR → IMU）= `[0.27255, -0.00053, 0.17954]` を得る。これは GRIL-Calib 論文 VI-B の「GT から RMSE 0.402 m ずらして初期並進 (0.6, 0.45, 0.6) を設定」と完全一致する。

`RMSE = √(((0.6−0.27255)² + (0.45+0.00053)² + (0.6−0.17954)²) / 3) = 0.403 m ≈ 0.402 m`

M2DGR が提供する IMU–LiDAR 外部パラメータの GT は、LI-Calib[52]の出力であることに注意。GRIL-Calib はこの値を GT として Table I の RMSE を測っている。

ちなみに M2DGR 論文では、カメラ↔IMU は Kalibr [53]、LiDAR↔カメラは Autoware [54]、IMU 内部ノイズは [51] でキャリブレーションされている。

[51] O. J. Woodman, "An introduction to inertial navigation," Univ. of Cambridge, Computer Laboratory, Tech. Rep. UCAM-CL-TR-696, Aug. 2007.（IMU 内部ノイズモデル（白色雑音・ランダムウォーク）の出典。実装は [imu_utils](https://github.com/gaowenliang/imu_utils) が対応）
[52] J. Lv, J. Xu, K. Hu, Y. Liu, and X. Zuo, "Targetless calibration of LiDAR-IMU system based on continuous-time batch estimation," in Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst., 2020, pp. 9968–9975.（= LI-Calib。IMU↔LiDAR 外部 GT の生成手法）
[53] P. Furgale, J. Rehder, and R. Siegwart, "Unified temporal and spatial calibration for multi-sensor systems," in Proc. IEEE/RSJ Int. Conf. Intell. Robots Syst., 2013, pp. 1280–1286.（= Kalibr。カメラ↔IMU 較正）
[54] S. Kato, E. Takeuchi, Y. Ishiguro, Y. Ninomiya, K. Takeda, and T. Hamada, "An open approach to autonomous vehicles," IEEE Micro, vol. 35, no. 6, pp. 60–68, Nov./Dec. 2015.（= Autoware。LiDAR↔カメラ較正）

#### GT vs 実行結果（LiDAR → IMU 表記）

GT: M2DGR 公式 / 実行結果: `result/GRIL_Calib_result.txt`

並進 (m)

| 軸 | GT（M2DGR 公式） | GRIL-Calib 実行結果 | 誤差 |
| --- | --- | --- | --- |
| x | 0.27255 | 0.214359 | −0.0582 |
| y | −0.00053 | 0.051815 | +0.0523 |
| z | 0.17954 | 0.178496 | −0.0010 |
| **RMSE** | — | — | **0.045** |

回転 (°)

| 軸 | GT（M2DGR 公式, 単位行列） | GRIL-Calib 実行結果 | 誤差 |
| --- | --- | --- | --- |
| roll | 0 | −0.129590 | −0.130 |
| pitch | 0 | 0.268340 | +0.268 |
| yaw | 0 | 0.579889 | +0.580 |
| **RMSE** | — | — | **0.376** |

論文 Table I（Gate 01, GRIL-Calib）の報告値との対照

| 指標 | 論文 Table I 報告 RMSE | 今回の実行結果（対 GT） |
| --- | --- | --- |
| 回転 (°) | 0.501 | 0.376 |
| 並進 (m) | 0.039 | 0.045 |

同オーダーで一致しており、較正は論文同等に成功している（差は再現実行による揺らぎの範囲）。

上記の回転・並進 RMSE は [`compute_rmse.py`](compute_rmse.py) で再計算できる（標準ライブラリのみ・numpy 不要、現時点では gate-01 のみ対応）。

```bash
python3 compute_rmse.py                     # デフォルトで result/GRIL_Calib_result.txt を読む
python3 compute_rmse.py path/to/result.txt  # 別の result ファイルを指定
```

### 削除

```bash
docker rm gril-calib-container
```

## KITTY-360

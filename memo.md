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
wget -O gt_gate01.txt "https://sjtueducn-my.sharepoint.com/:t:/g/personal/594666_sjtu_edu_cn/EfipLVtlRChHvwklkDPylPgBSIQry0_JdfqH-6DaxWCaNA?e=idVsY4&download=1"

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

### 評価

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

### 削除

```bash
docker rm gril-calib-container
```

## KITTY-360

#!/usr/bin/env python3
"""GRIL-Calib の推定外部パラメータ（result/GRIL_Calib_result.txt）を
M2DGR 公式 GT と突き合わせ、回転・並進の RMSE を計算する。

現時点では M2DGR gate-01 のみ対応。

GT の出所と座標系について:
  M2DGR 公式 calibration_results.txt の末尾「Handsfree IMU」セクションは
  `Extrinsic [to LIDAR]`（IMU -> LiDAR 方向）で
      translation = [-0.27255, 0.00053, -0.17954], rotation = 単位行列
  と記載されている。一方 GRIL_Calib_result.txt は LiDAR -> IMU 方向で値を
  出力するため、比較するには向きを揃える必要がある。ここでは GT を
  LiDAR -> IMU 方向に変換して保持する。回転が単位行列なので、逆変換の並進
  -R^T t は -t に帰着し、各成分の符号反転だけで済む:
      translation(LiDAR -> IMU) = [0.27255, -0.00053, 0.17954]
      rotation(LiDAR -> IMU)    = [0, 0, 0]  (deg)
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

# GT は result ファイルと同じ LiDAR -> IMU 方向で定義する（上記 docstring 参照）。
GROUND_TRUTH = {
    "m2dgr/gate01": {
        "rotation_deg": (0.0, 0.0, 0.0),                # roll, pitch, yaw
        "translation_m": (0.27255, -0.00053, 0.17954),  # x, y, z
    },
}

DEFAULT_RESULT = Path(__file__).parent / "result" / "GRIL_Calib_result.txt"


def parse_result(path: Path) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """result ファイルから LiDAR -> IMU の回転(deg)と並進(m)を読み取る。"""
    text = path.read_text()

    def grab(label: str) -> tuple[float, ...]:
        match = re.search(rf"{label}.*?=\s*(.+)", text)
        if not match:
            raise ValueError(f"'{label}' 行が {path} に見つからない")
        return tuple(float(v) for v in match.group(1).split())

    rotation = grab(r"Rotation LiDAR to IMU \(degree\)")
    translation = grab(r"Translation LiDAR to IMU \(meter\)")
    return rotation, translation


def rmse(estimate: tuple[float, ...], truth: tuple[float, ...]) -> tuple[float, list[float]]:
    """各成分誤差の二乗平均平方根（RMSE）と、成分ごとの誤差を返す。"""
    errors = [e - t for e, t in zip(estimate, truth)]
    value = math.sqrt(sum(err * err for err in errors) / len(errors))
    return value, errors


def report(name: str, unit: str, axes: tuple[str, ...],
           estimate: tuple[float, ...], truth: tuple[float, ...]) -> float:
    value, errors = rmse(estimate, truth)
    print(f"\n{name} ({unit})")
    print(f"  {'軸':<6}{'GT':>12}{'推定':>12}{'誤差':>12}")
    for axis, gt, est, err in zip(axes, truth, estimate, errors):
        print(f"  {axis:<6}{gt:>12.5f}{est:>12.5f}{err:>+12.5f}")
    print(f"  RMSE = {value:.4f} {unit}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "result", nargs="?", type=Path, default=DEFAULT_RESULT,
        help=f"GRIL_Calib_result.txt のパス (default: {DEFAULT_RESULT})",
    )
    parser.add_argument(
        "--sequence", default="m2dgr/gate01", choices=sorted(GROUND_TRUTH),
        help="対象シーケンス (default: m2dgr/gate01)",
    )
    args = parser.parse_args()

    gt = GROUND_TRUTH[args.sequence]
    rotation_est, translation_est = parse_result(args.result)

    print(f"sequence : {args.sequence}")
    print(f"result   : {args.result}")
    report("回転", "deg", ("roll", "pitch", "yaw"), rotation_est, gt["rotation_deg"])
    report("並進", "m", ("x", "y", "z"), translation_est, gt["translation_m"])


if __name__ == "__main__":
    main()

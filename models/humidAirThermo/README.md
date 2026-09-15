# 湿空气与物种热力学

| 文件 | 用途 |
|---|---|
| `IAPWS_G11_2015_VirialFugacity.pdf` | 湿空气中水蒸气逸度；用于 `S=fWater/fSaturation` |
| `IAPWS_G8_2010_HumidAirEOS.pdf` | 平衡湿空气 Helmholtz EOS；用于物性对照，不直接消除亚稳过饱和状态 |
| `IAPWS_R1_2014_SurfaceTension.pdf` | 水的温变表面张力 |
| `NASA_TP_2002_211556_SpeciesThermo.pdf` | NASA 物种 `Cp/h/s` 多项式及参考态 |
| `NASA_TP_1466_WETAIR.pdf` | 干空气－水混合物热力学与输运基准 |

这些资料共同约束 `SpeciesThermo`、`HumidAirEOS`、`SaturationProperties` 和
`SurfaceTensionProperties`，但不规定相变时间积分算法。

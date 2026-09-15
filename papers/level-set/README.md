# Level Set + GFM 论文目录

本文档对应 `papers/levelSet_GFM_multiphase_research.md` 中的核心论文清单。

## 已保存 PDF

| 文件 | 论文 | 来源 |
|---|---|---|
| `Osher_Sethian_1988_levelSet_origin.pdf` | Osher & Sethian, 1988, *Fronts propagating with curvature-dependent speed: Algorithms based on Hamilton-Jacobi formulations*, DOI: [10.1016/0021-9991(88)90002-2](https://doi.org/10.1016/0021-9991(88)90002-2) | NASA NTRS open PDF |
| `Sussman_Fatemi_1999_redistancing.pdf` | Sussman & Fatemi, 1999, *An Efficient, Interface-Preserving Level Set Redistancing Algorithm and Its Application to Interfacial Incompressible Fluid Flow*, DOI: [10.1137/S1064827596298245](https://doi.org/10.1137/S1064827596298245) | HAL open manuscript |
| `Kang_Fedkiw_Liu_2000_multiphase_incompressible_GFM.pdf` | Kang, Fedkiw & Liu, 2000, *A Boundary Condition Capturing Method for Multiphase Incompressible Flow*, DOI: [10.1023/A:1011178417620](https://doi.org/10.1023/A:1011178417620) | Springer PDF |

## 待补 PDF

以下条目已记录 DOI 和出版页，但当前没有从公开/出版方直链拿到可用 PDF。下载尝试中，SIAM 直链返回 HTML 页面；Elsevier API 返回 `406`，所以没有把这些 HTML/错误响应保存为 PDF。

| 论文 | DOI / 出版页 | 备注 |
|---|---|---|
| Sussman, Smereka & Osher, 1994, *A Level Set Approach for Computing Solutions to Incompressible Two-Phase Flow* | [10.1006/jcph.1994.1155](https://doi.org/10.1006/jcph.1994.1155) | 待补全文 PDF |
| Chang, Hou, Merriman & Osher, 1996, *A Level Set Formulation of Eulerian Interface Capturing Methods for Incompressible Fluid Flows* | [10.1006/jcph.1996.0072](https://doi.org/10.1006/jcph.1996.0072) | 待补全文 PDF |
| Jiang & Peng, 2000, *Weighted ENO Schemes for Hamilton-Jacobi Equations* | [10.1137/S106482759732455X](https://doi.org/10.1137/S106482759732455X) | SIAM 直链未返回 PDF |
| Fedkiw, Aslam, Merriman & Osher, 1999, *A Non-oscillatory Eulerian Approach to Interfaces in Multimaterial Flows (the Ghost Fluid Method)* | [10.1006/jcph.1999.6236](https://doi.org/10.1006/jcph.1999.6236) | 待补全文 PDF |
| Liu, Fedkiw & Kang, 2000, *A Boundary Condition Capturing Method for Poisson's Equation on Irregular Domains* | [10.1006/jcph.2000.6444](https://doi.org/10.1006/jcph.2000.6444) | 待补全文 PDF |
| Enright, Fedkiw, Ferziger & Mitchell, 2002, *A Hybrid Particle Level Set Method for Improved Interface Capturing* | [10.1006/jcph.2002.7166](https://doi.org/10.1006/jcph.2002.7166) | 待补全文 PDF |
| Aslam, 2004, *A partial differential equation approach to multidimensional extrapolation* | [10.1016/j.jcp.2003.08.001](https://doi.org/10.1016/j.jcp.2003.08.001) | 待补全文 PDF |

## 使用建议

第一版实现优先精读本目录已保存的三篇：

1. `Osher_Sethian_1988_levelSet_origin.pdf`：Level Set 的 Hamilton-Jacobi 基础。
2. `Sussman_Fatemi_1999_redistancing.pdf`：重初始化和界面保持。
3. `Kang_Fedkiw_Liu_2000_multiphase_incompressible_GFM.pdf`：最接近 `sonicSolver` 压力基多相路线的 Level Set + GFM + projection 框架。

其它待补论文的算法要点已先整理在 `../levelSet_GFM_multiphase_research.md`，后续拿到 PDF 后可直接放到本目录，并更新上表。

# 多块共点 MPI

- `hypre_ReferenceManual.pdf`：HYPRE IJ/ParCSR 接口、global row ownership、矩阵装配
  与求解器配置参考。
- 架构目标：三块、五块或任意 N 共点映射到一个 global DOF；显式残差按对偶体积
  片段装配，隐式矩阵按 canonical row 累加。
- HYPRE 资料只约束线性接口；共享点拓扑、junction 守恒公式和 WENO `StencilPath`
  仍由 sonicSolver 的离散契约定义。

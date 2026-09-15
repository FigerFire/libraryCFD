# 干空气＋水蒸气，无凝结

主要物性资料位于 [`../../models/humidAirThermo`](../../models/humidAirThermo/README.md)：

- NASA WETAIR：混合物热力学/输运对照；
- NASA species thermo：干空气组分和水蒸气的 `Cp/h/e`；
- IAPWS G11/G8：逸度和非理想湿空气的后续对照。

该 case 关闭凝结，只验证组分守恒、质量分数、混合 EOS、声速和总能量。

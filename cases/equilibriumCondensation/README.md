# 平衡凝结

物性依据使用 [`../../models/humidAirThermo`](../../models/humidAirThermo/README.md)。
流动/凝结对照可参考 [`../lavalNozzle`](../lavalNozzle/README.md)。

第一项验证应是绝热定容单元：守恒 `rhoWaterTotal` 和 `rhoE`，联立求解平衡温度与
凝结量并满足逸度平衡。禁止在旧温度下直接截断 `Yv`。

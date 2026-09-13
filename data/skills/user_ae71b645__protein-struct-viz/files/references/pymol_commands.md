# PyMOL 命令参考

## 基本命令

### 结构加载
```
fetch <pdb_id>          # 从 RCSB PDB 下载
cmd.load <file.pdb>     # 加载本地文件
cmd.read_pdbstr <str>   # 从 PDB 字符串加载
```

### 选择语法
```
selection-name: selection-expression

# 选择操作符
and         # 交集
or          # 并集
not         # 差集
around X    # X 埃（Angstrom）范围内的原子
expand X    # 将选择范围扩展 X 埃
byres       # 扩展到完整残基
```

### 选择示例
```
chain A                 # 链 A 中的所有原子
resi 145                # 残基编号 145
resn ASP                # 所有天冬氨酸（ASP）残基
name CA                 # 所有 α 碳原子
chain A and resi 145    # 链 A 中的残基 145
resi 145-160            # 残基编号范围
center chain A          # 链 A 的中心
```

## 表示样式命令

```
show <representation> [, <selection>]
hide <representation> [, <selection>]

# 表示样式：
lines       # 成键原子间的线条
sticks      # 化学键的圆柱体（棒状）
spheres     # 原子的球体（球状）
surface     # 溶剂可及表面
mesh        # 网格表面
dots        # 点状表面
cartoon     # 二级结构卡通图
ribbon      # 平滑带状图
cells       # 晶胞
```

## 颜色命令

```
color <color> [, <selection>]

# 预定义颜色：
red, green, blue, yellow, magenta, cyan
orange, salmon, lime, pink, slate, teal
gray, white, black, wheat, paleyellow

# 配色方案：
util.cbc()              # 按链着色
cmd.spectrum()          # 彩虹渐变
cmd.spectrum('b')       # 按 B 因子着色
```

## 视角设置

```
bg_color <color>        # 背景颜色
zoom <selection>        # 缩放到选择区域
center <selection>      # 居中视角
reset                   # 重置视角
orient <selection>      # 定向选择区域
```

## 渲染设置

```
set ray_trace_mode, 0   # 普通渲染
set ray_trace_mode, 1   # 普通 + 阴影
set ray_trace_mode, 2   # 普通 + 黑色轮廓线
set ray_trace_mode, 3   # 快速轮廓模式

set antialias, 2        # 抗锯齿（0-4）
set ray_shadows, 0      # 关闭阴影
set ray_shadows, 1      # 开启阴影

ray [width, height]     # 光线追踪渲染图像
png <filename>          # 保存图像
```

## 原子属性

```
resi    # 残基编号
resn    # 残基名称（三字母代码）
name    # 原子名称（CA、CB、N、O 等）
elem    # 元素符号
chain   # 链标识符
seg     # 片段标识符
alt     # 备选构象
```

## 常见残基名称

| 代码 | 名称          | 代码 | 名称          |
|------|---------------|------|---------------|
| ALA  | 丙氨酸       | LEU  | 亮氨酸       |
| ARG  | 精氨酸       | LYS  | 赖氨酸       |
| ASN  | 天冬酰胺     | MET  | 甲硫氨酸     |
| ASP  | 天冬氨酸     | PHE  | 苯丙氨酸     |
| CYS  | 半胱氨酸     | PRO  | 脯氨酸       |
| GLN  | 谷氨酰胺     | SER  | 丝氨酸       |
| GLU  | 谷氨酸       | THR  | 苏氨酸       |
| GLY  | 甘氨酸       | TRP  | 色氨酸       |
| HIS  | 组氨酸       | TYR  | 酪氨酸       |
| ILE  | 异亮氨酸     | VAL  | 缬氨酸       |

## 使用技巧

1. 使用 `cmd.dss()` 分配二级结构
2. 使用 `util.cbc()` 进行按链着色
3. 将 `center` 和 `zoom` 搭配使用以获得聚焦视角
4. 使用 `save session.pse` 保存会话
5. 使用 `label sele and name CA, '%s %s' % (resn, resi)` 为残基添加标签

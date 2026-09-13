---
name: molecular-dynamics
description: 用 OpenMM 与 MDAnalysis 运行并分析分子动力学模拟。搭建蛋白质/小分子体系、定义力场、运行能量最小化与生产 MD、分析轨迹（RMSD、RMSF、接触图、自由能面）。用于结构生物学、药物结合与生物物理学。
license: MIT
metadata: {"version": "1.0.0", "skill-author": "Kuan-lin Huang"}
---

# 分子动力学

## 概述

分子动力学（MD）模拟通过对牛顿运动方程积分，对分子系统的时间演化进行计算机建模。本 skill 涵盖两个互补的工具：

- **OpenMM**（https://openmm.org/）：高性能 MD 模拟引擎，支持 GPU、Python API 与灵活的力场支持
- **MDAnalysis**（https://mdanalysis.org/）：用于读取、写入并分析所有主流模拟包产生的 MD 轨迹的 Python 库

**安装：**
```bash
conda install -c conda-forge openmm mdanalysis nglview
# 或
pip install openmm mdanalysis
```

## 何时使用本 Skill

在以下场景使用分子动力学：

- **蛋白质稳定性分析**：突变如何影响蛋白质动力学？
- **药物结合模拟**：表征配体的结合模式与停留时间
- **构象采样**：探索蛋白质灵活性与构象变化
- **蛋白质-蛋白质相互作用**：建模界面动力学与结合 energetics
- **RMSD/RMSF 分析**：从参考结构量化结构涨落
- **自由能估算**：计算结合自由能或构象自由能
- **膜模拟**：在脂质双分子层中建模蛋白质
- **固有无序蛋白**：研究 IDR 构象系综

## 核心工作流：OpenMM 模拟

### 1. 体系准备

```python
from openmm.app import *
from openmm import *
from openmm.unit import *
import sys

def prepare_system_from_pdb(pdb_file, forcefield_name="amber14-all.xml",
                              water_model="amber14/tip3pfb.xml"):
    """
    从 PDB 文件准备一个 OpenMM 系统。

    Args:
        pdb_file: 清洗过的 PDB 文件路径（原始 PDB 用 PDBFixer）
        forcefield_name: 力场 XML 文件
        water_model: 水模型 XML 文件

    Returns:
        pdb, forcefield, system, topology
    """
    # 加载 PDB
    pdb = PDBFile(pdb_file)

    # 加载力场
    forcefield = ForceField(forcefield_name, water_model)

    # 加氢原子并溶剂化
    modeller = Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens(forcefield)

    # 加溶剂盒（10 Å 填充，150 mM NaCl）
    modeller.addSolvent(
        forcefield,
        model='tip3p',
        padding=10*angstroms,
        ionicStrength=0.15*molar
    )

    print(f"System: {modeller.topology.getNumAtoms()} atoms, "
          f"{modeller.topology.getNumResidues()} residues")

    # 创建系统
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=PME,         # 长程静电用 Particle Mesh Ewald
        nonbondedCutoff=1.0*nanometer,
        constraints=HBonds,           # 约束氢键（允许 2 fs 步长）
        rigidWater=True,
        ewaldErrorTolerance=0.0005
    )

    return modeller, system
```

### 2. 能量最小化

```python
from openmm.app import *
from openmm import *
from openmm.unit import *

def minimize_energy(modeller, system, output_pdb="minimized.pdb",
                     max_iterations=1000, tolerance=10.0):
    """
    对体系进行能量最小化以去除空间位阻。

    Args:
        modeller: 含拓扑与位置的 Modeller 对象
        system: OpenMM System
        output_pdb: 保存最小化结构的路径
        max_iterations: 最大化步数
        tolerance: 收敛判据，单位 kJ/mol/nm

    Returns:
        simulation 对象（含最小化位置）
    """
    # 设置积分器（对最小化不重要）
    integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.004*picoseconds)

    # 创建模拟
    # 若可用则用 GPU（CUDA 或 OpenCL），回退到 CPU
    try:
        platform = Platform.getPlatformByName('CUDA')
        properties = {'DeviceIndex': '0', 'Precision': 'mixed'}
    except Exception:
        try:
            platform = Platform.getPlatformByName('OpenCL')
            properties = {}
        except Exception:
            platform = Platform.getPlatformByName('CPU')
            properties = {}

    simulation = Simulation(
        modeller.topology, system, integrator,
        platform, properties
    )
    simulation.context.setPositions(modeller.positions)

    # 检查初始能量
    state = simulation.context.getState(getEnergy=True)
    print(f"Initial energy: {state.getPotentialEnergy()}")

    # 最小化
    simulation.minimizeEnergy(
        tolerance=tolerance*kilojoules_per_mole/nanometer,
        maxIterations=max_iterations
    )

    state = simulation.context.getState(getEnergy=True, getPositions=True)
    print(f"Minimized energy: {state.getPotentialEnergy()}")

    # 保存最小化结构
    with open(output_pdb, 'w') as f:
        PDBFile.writeFile(simulation.topology, state.getPositions(), f)

    return simulation
```

### 3. NVT 平衡

```python
from openmm.app import *
from openmm import *
from openmm.unit import *

def run_nvt_equilibration(simulation, n_steps=50000, temperature=300,
                            report_interval=1000, output_prefix="nvt"):
    """
    NVT 平衡：恒定 N、V、T。
    将速度平衡到目标温度。

    Args:
        simulation: OpenMM Simulation（最小化后）
        n_steps: MD 步数（50000 × 2fs = 100 ps）
        temperature: 温度，单位 Kelvin
        report_interval: 数据报告间隔步数
        output_prefix: 轨迹与日志的文件前缀
    """
    # NVT 期间对骨架加位置约束
    # （可选：约束重原子）

    # 设置温度
    simulation.context.setVelocitiesToTemperature(temperature*kelvin)

    # 加 reporter
    simulation.reporters = []

    # 日志文件
    simulation.reporters.append(
        StateDataReporter(
            f"{output_prefix}_log.txt",
            report_interval,
            step=True,
            potentialEnergy=True,
            kineticEnergy=True,
            temperature=True,
            volume=True,
            speed=True
        )
    )

    # DCD 轨迹（紧凑二进制格式）
    simulation.reporters.append(
        DCDReporter(f"{output_prefix}_traj.dcd", report_interval)
    )

    print(f"Running NVT equilibration: {n_steps} steps ({n_steps*2/1000:.1f} ps)")
    simulation.step(n_steps)
    print("NVT equilibration complete")

    return simulation
```

### 4. NPT 平衡与生产

```python
def run_npt_production(simulation, n_steps=500000, temperature=300, pressure=1.0,
                        report_interval=5000, output_prefix="npt"):
    """
    NPT 生产运行：恒定 N、P、T。

    Args:
        n_steps: 生产步数（500000 × 2fs = 1 ns）
        temperature: 温度，单位 Kelvin
        pressure: 压力，单位 bar
        report_interval: 报告间隔步数
    """
    # 加 Monte Carlo 气压计控制压力
    system = simulation.context.getSystem()
    system.addForce(MonteCarloBarostat(pressure*bar, temperature*kelvin, 25))
    simulation.context.reinitialize(preserveState=True)

    # 更新 reporter
    simulation.reporters = []
    simulation.reporters.append(
        StateDataReporter(
            f"{output_prefix}_log.txt",
            report_interval,
            step=True,
            potentialEnergy=True,
            temperature=True,
            density=True,
            speed=True
        )
    )
    simulation.reporters.append(
        DCDReporter(f"{output_prefix}_traj.dcd", report_interval)
    )

    # 保存检查点
    simulation.reporters.append(
        CheckpointReporter(f"{output_prefix}_checkpoint.chk", 50000)
    )

    print(f"Running NPT production: {n_steps} steps ({n_steps*2/1000000:.2f} ns)")
    simulation.step(n_steps)
    print("Production MD complete")
    return simulation
```

## 用 MDAnalysis 分析轨迹

### 1. 加载轨迹

```python
import MDAnalysis as mda
from MDAnalysis.analysis import rms, align, contacts
import numpy as np
import matplotlib.pyplot as plt

def load_trajectory(topology_file, trajectory_file):
    """
    用 MDAnalysis 加载一条 MD 轨迹。

    Args:
        topology_file: PDB、PSF 或其他拓扑文件
        trajectory_file: DCD、XTC、TRR 或其他轨迹
    """
    u = mda.Universe(topology_file, trajectory_file)
    print(f"Universe: {u.atoms.n_atoms} atoms, {u.trajectory.n_frames} frames")
    print(f"Time range: 0 to {u.trajectory.totaltime:.0f} ps")
    return u
```

### 2. RMSD 分析

```python
def compute_rmsd(u, selection="backbone", reference_frame=0):
    """
    计算选定原子相对于参考帧的 RMSD。

    Args:
        u: MDAnalysis Universe
        selection: 原子选择字符串（MDAnalysis 语法）
        reference_frame: 参考结构的帧索引

    Returns:
        numpy 数组，含 (time, rmsd) 值
    """
    # 对齐轨迹以最小化 RMSD
    aligner = align.AlignTraj(u, u, select=selection, in_memory=True)
    aligner.run()

    # 计算 RMSD
    R = rms.RMSD(u, select=selection, ref_frame=reference_frame)
    R.run()

    rmsd_data = R.results.rmsd  # 列：frame, time, RMSD
    return rmsd_data

def plot_rmsd(rmsd_data, title="RMSD over time", output_file="rmsd.png"):
    """绘制模拟时间上的 RMSD。"""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(rmsd_data[:, 1] / 1000, rmsd_data[:, 2], 'b-', linewidth=0.5)
    ax.set_xlabel("Time (ns)")
    ax.set_ylabel("RMSD (Å)")
    ax.set_title(title)
    ax.axhline(rmsd_data[:, 2].mean(), color='r', linestyle='--',
               label=f'Mean: {rmsd_data[:, 2].mean():.2f} Å')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    return fig
```

### 3. RMSF 分析（逐残基灵活性）

```python
def compute_rmsf(u, selection="backbone", start_frame=0):
    """
    计算逐残基 RMSF（灵活性）。

    Returns:
        resids, rmsf_values 数组
    """
    # 选择原子
    atoms = u.select_atoms(selection)

    # 计算 RMSF
    R = rms.RMSF(atoms)
    R.run(start=start_frame)

    # 按残基平均
    resids = []
    rmsf_per_res = []
    for res in u.select_atoms(selection).residues:
        res_atoms = res.atoms.intersection(atoms)
        if len(res_atoms) > 0:
            resids.append(res.resid)
            rmsf_per_res.append(R.results.rmsf[res_atoms.indices].mean())

    return np.array(resids), np.array(rmsf_per_res)
```

### 4. 蛋白-配体接触

```python
def analyze_contacts(u, protein_sel="protein", ligand_sel="resname LIG",
                      radius=4.5, start_frame=0):
    """
    在轨迹上追踪蛋白-配体接触。

    Args:
        radius: 接触距离截断，单位埃
    """
    protein = u.select_atoms(protein_sel)
    ligand = u.select_atoms(ligand_sel)

    contact_frames = []
    for ts in u.trajectory[start_frame:]:
        # 找到配体半径内的蛋白原子
        distances = contacts.contact_matrix(
            protein.positions, ligand.positions, radius
        )
        contact_residues = set()
        for i in range(distances.shape[0]):
            if distances[i].any():
                contact_residues.add(protein.atoms[i].resid)
        contact_frames.append(contact_residues)

    return contact_frames
```

## 力场选择指南

| 系统 | 推荐力场 | 水模型 |
|--------|------------------------|-------------|
| 标准蛋白 | AMBER14 (`amber14-all.xml`) | TIP3P-FB |
| 蛋白 + 小分子 | AMBER14 + GAFF2 | TIP3P-FB |
| 膜蛋白 | CHARMM36m | TIP3P |
| 核酸 | AMBER99-bsc1 或 AMBER14 | TIP3P |
| 无序蛋白 | ff19SB 或 CHARMM36m | TIP3P |

## 体系准备工具

### PDBFixer（用于原始 PDB 文件）

```python
from pdbfixer import PDBFixer
from openmm.app import PDBFile

def fix_pdb(input_pdb, output_pdb, ph=7.0):
    """修复常见 PDB 问题：缺失残基、原子，加 H，标准化。"""
    fixer = PDBFixer(filename=input_pdb)
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(True)    # 去除水/配体
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(ph)

    with open(output_pdb, 'w') as f:
        PDBFile.writeFile(fixer.topology, fixer.positions, f)

    return output_pdb
```

### 用于小分子的 GAFF2（通过 OpenFF Toolkit）

```python
# 配体参数化使用 OpenFF toolkit 或 ACPYPE
# pip install openff-toolkit
from openff.toolkit import Molecule, ForceField as OFFForceField
from openff.interchange import Interchange

def parameterize_ligand(smiles, ff_name="openff-2.0.0.offxml"):
    """为小分子生成 GAFF2/OpenFF 参数。"""
    mol = Molecule.from_smiles(smiles)
    mol.generate_conformers(n_conformers=1)

    off_ff = OFFForceField(ff_name)
    interchange = off_ff.create_interchange(mol.to_topology())
    return interchange
```

## 最佳实践

- **MD 前始终最小化**：原始 PDB 结构存在空间位阻
- **生产前先平衡**：NVT（50–100 ps）→ NPT（100–500 ps）→ 生产
- **使用 GPU**：模拟在 GPU 上快 10–100×（CUDA/OpenCL）
- **HBonds 约束下用 2 fs 步长**：标准；用 HMR（氢质量重分配）可到 4 fs
- **只分析已平衡的轨迹**：丢弃前 20–50% 作为平衡阶段
- **保存检查点**：MD 运行可能失败；检查点允许重启
- **周期性边界条件**：溶剂化体系所必需
- **静电用 PME**：对带电体系比截断方法更准确

## 附加资源

- **OpenMM 文档**：https://openmm.org/documentation.html
- **MDAnalysis 用户指南**：https://docs.mdanalysis.org/
- **GROMACS**（替代 MD 引擎）：https://manual.gromacs.org/
- **NAMD**（替代）：https://www.ks.uiuc.edu/Research/namd/
- **CHARMM-GUI**（基于 Web 的体系构建器）：https://charmm-gui.org/
- **AmberTools**（免费 Amber 工具）：https://ambermd.org/AmberTools.php
- **OpenMM 论文**：Eastman P et al. (2017) PLOS Computational Biology. PMID: 28278240
- **MDAnalysis 论文**：Michaud-Agrawal N et al. (2011) J Computational Chemistry. PMID: 21500218

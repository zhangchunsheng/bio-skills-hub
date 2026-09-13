# 故障报告生成示例

## 示例1：完整的markdown转HTML流程

### 输入markdown文件

```markdown
## 环境信息
- 客户名称：某行业客户
- 项目名称：某客户云平台项目
- 故障时间：2026年6月15日 15:08
- 云平台版本：ZStack Cloud 4.4.46 c76
- 存储系统：ZStone 4.2.4

## 故障现象
2026年6月15日15:08，监控发现**5个磁盘显示离线状态**，涉及多个节点的OSD服务异常。

![磁盘离线](https://obsidian-1305309714.cos.ap-chengdu.myqcloud.com/image/image-2026-06-15-15-08-00-tLpkelAW.png)

## 详细排查经过

### 节点 compute-node-01 (SN: SN-001)
- **受影响OSD**：osd.20（SDK磁盘）
- **问题描述**：
  - 底层lsblk只能看到9块HDD盘
  - RAID卡中可以查看到共10块7.3T HDD
  - 存在磁盘识别不一致问题

![RAID配置](https://obsidian-1305309714.cos.ap-chengdu.myqcloud.com/image/image-2026-06-15-15-19-02-HaXaGo6H.png)

**排查结论**：当前现象表现为操作系统层与RAID控制器层的磁盘识别结果不一致，需优先按RAID控制器固件/驱动兼容性方向继续核验。

### 节点 compute-node-02 (SN: SN-002)
- **受影响OSD**：osd.42、osd.43、osd.46（均为SDE磁盘）
- **问题描述**：
  - lsblk只能查看到7块HDD盘
  - RAID卡上能看到10块磁盘
  - 底层无法查看，但RAID内能查看

![RAID图1](https://obsidian-1305309714.cos.ap-chengdu.myqcloud.com/image/image-2026-06-15-15-32-20-z9Fk8Zee.png)
![RAID图2](https://obsidian-1305309714.cos.ap-chengdu.myqcloud.com/image/image-2026-06-15-15-34-38-1OdpJzAm.png)

**排查结论**：当前节点存在“底层不可见、RAID层可见”的一致性异常，结合现象判断，问题更偏向底层硬件链路或控制器识别异常，而非上层业务负载导致。

## 故障结论

### 已确认原因
1. **多节点磁盘识别异常**：经现场排查确认，compute-node-01和compute-node-02节点存在操作系统层与RAID控制器层磁盘识别结果不一致的情况，该异常与磁盘离线现象存在直接对应关系。
2. **数据库残留影响状态判断**：经核查，compute-node-03节点存在历史OSD数据库残留信息，对当前磁盘状态识别造成干扰。
3. **备份节点硬件故障**：经硬件侧日志及RAID状态核验，备份节点 backup-node-01 的 RAID5 组内存在物理磁盘故障。

### 初步判断
- 结合多节点一致性现象与底层识别表现，当前证据指向RAID控制器固件/驱动兼容性问题的可能性较高，建议结合硬件厂商进一步完成版本匹配核验。

### 排除因素
- ✓ 存储平台当时没有大流量出现
- ✓ 云平台虚拟机监控显示CPU和磁盘负载均不高

## 处置与治理方案

### 临时处置方案（建议在维护窗口内执行）
- 建议对 compute-node-01 和 compute-node-02 节点安排重启验证，以确认磁盘识别异常是否可在系统重载后恢复。
- 建议对 compute-node-03 节点执行 OSD 数据库残留清理及一致性复核，避免历史残留信息继续影响当前状态判断。
- 建议尽快更换 backup-node-01 的故障磁盘，并在更换完成后核验 RAID 组状态与数据同步情况。

### 长期治理方案（持续改进）
- 建议联合硬件厂商对相关节点 RAID 控制器固件、驱动与当前操作系统版本的兼容性进行专项核查，并形成升级计划。
- 建议对现网节点 RAID 配置、磁盘健康状态及固件版本开展一次专项巡检，提前识别同类隐患。
- 建议补充磁盘与控制器健康监控、告警与巡检机制，完善硬件异常场景下的标准处置预案。
- 建议建立定期固件评估与升级机制，并同步完善运维侧巡检清单与故障复盘流程。
```

### 生成的HTML关键片段

#### 1. 基本信息表
```html
<div class="basic-info-section">
    <div class="section-title editable">故障基本信息</div>
    <table class="info-table">
        <tr>
            <td class="label">项目名称</td>
            <td class="value editable" colspan="3">某客户云平台项目</td>
        </tr>
        <tr>
            <td class="label">客户名称</td>
            <td class="value editable" colspan="3">某行业客户</td>
        </tr>
        <tr>
            <td class="label">故障影响和范围</td>
            <td class="value editable" colspan="3">5个磁盘显示离线状态，涉及 compute-node-01、compute-node-02、compute-node-03 及备份节点 backup-node-01</td>
        </tr>
        <tr>
            <td class="label">软件产品</td>
            <td class="value editable">ZStack Cloud / ZStone</td>
            <td class="label">版本号</td>
            <td class="value editable">ZStack Cloud 4.4.46 c76 / ZStone 4.2.4</td>
        </tr>
        <tr>
            <td class="label">故障发生时间</td>
            <td class="value editable">2026年6月15日 15:08</td>
            <td class="label">业务恢复时间</td>
            <td class="value editable">待确认</td>
        </tr>
        <!-- 其他行... -->
    </table>
</div>
```

#### 2. 故障现象
```html
<div class="content-section">
    <div class="section-header editable">一、故障情况描述</div>
    
    <div class="highlight-box">
        <p class="editable"><strong>故障现象：</strong>2026年6月15日15:08，监控发现<strong>5个磁盘显示离线状态</strong>，涉及多个节点的OSD服务异常。</p>
    </div>
    
    <div class="image-container" style="max-width: 900px; margin: 25px auto;">
        <img src="https://obsidian-1305309714.cos.ap-chengdu.myqcloud.com/image/image-2026-06-15-15-08-00-tLpkelAW.png" alt="磁盘离线状态截图">
        <div class="image-caption editable">图1：磁盘离线状态监控截图</div>
    </div>
    
    <div class="subsection-title editable">详细排查经过</div>
```

#### 3. 第一个节点详情
```html
    <div class="node-detail">
        <h4 class="editable">1. 节点 compute-node-01 (SN: SN-001)</h4>
        <div class="detail-item">
            <strong>受影响OSD：</strong><span class="editable">osd.20（SDK磁盘）</span>
        </div>
        <div class="detail-item">
            <strong>问题描述：</strong>
            <ul class="editable">
                <li>底层lsblk只能看到9块HDD盘</li>
                <li>RAID卡中可以查看到共10块7.3T HDD</li>
                <li>存在磁盘识别不一致问题</li>
            </ul>
        </div>
        
        <div class="image-container" style="max-width: 800px; margin: 20px auto;">
            <img src="https://obsidian-1305309714.cos.ap-chengdu.myqcloud.com/image/image-2026-06-15-15-19-02-HaXaGo6H.png" alt="compute-node-01 RAID配置">
            <div class="image-caption editable">图2：compute-node-01 节点 RAID 配置信息</div>
        </div>
        
        <div class="recommendation-box">
            <strong>排查结论：</strong><span class="editable">当前现象表现为操作系统层与RAID控制器层的磁盘识别结果不一致，需优先按RAID控制器固件/驱动兼容性方向继续核验。</span>
        </div>
    </div>
```

#### 4. 第二个节点（双图并排）
```html
    <div class="node-detail">
        <h4 class="editable">2. 节点 compute-node-02 (SN: SN-002)</h4>
        <div class="detail-item">
            <strong>受影响OSD：</strong><span class="editable">osd.42、osd.43、osd.46（均为SDE磁盘）</span>
        </div>
        <div class="detail-item">
            <strong>问题描述：</strong>
            <ul class="editable">
                <li>lsblk只能查看到7块HDD盘</li>
                <li>RAID卡上能看到10块磁盘</li>
                <li>底层无法查看，但RAID内能查看</li>
            </ul>
        </div>
        
        <div class="image-grid">
            <div class="image-item">
                <img src="https://obsidian-1305309714.cos.ap-chengdu.myqcloud.com/image/image-2026-06-15-15-32-20-z9Fk8Zee.png" alt="compute-node-02 RAID配置图1">
                <div class="image-caption editable">图3：compute-node-02 节点 RAID 配置信息（1）</div>
            </div>
            <div class="image-item">
                <img src="https://obsidian-1305309714.cos.ap-chengdu.myqcloud.com/image/image-2026-06-15-15-34-38-1OdpJzAm.png" alt="compute-node-02 RAID配置图2">
                <div class="image-caption editable">图4：compute-node-02 节点 RAID 配置信息（2）</div>
            </div>
        </div>
        
        <div class="recommendation-box">
            <strong>排查结论：</strong><span class="editable">当前节点存在“底层不可见、RAID层可见”的一致性异常，结合现象判断，问题更偏向底层硬件链路或控制器识别异常，而非上层业务负载导致。</span>
        </div>
    </div>
```

#### 5. 原因分析
```html
<div class="content-section">
    <div class="section-header editable">二、原因分析</div>
    
    <div class="analysis-section">
        <h3 class="editable">已确认原因</h3>
        <ol class="editable">
            <li><strong>多节点磁盘识别异常：</strong>经现场排查确认，compute-node-01 和 compute-node-02 节点存在底层系统与 RAID 控制器层磁盘识别结果不一致的情况。操作系统层无法完整识别磁盘，而 RAID 控制器侧可查看到对应设备，说明异常链路集中在底层硬件识别或控制器兼容性侧。</li>
            
            <li><strong>数据库残留影响状态判断：</strong>经核查，compute-node-03 节点存在历史 OSD 数据库残留信息，对当前磁盘状态识别造成干扰。</li>
            
            <li><strong>备份节点硬件故障：</strong>备份节点 backup-node-01 的 RAID5 组内存在物理磁盘故障（示例槽位），该异常与当前节点告警状态相互印证。</li>
        </ol>
    </div>

    <div class="analysis-section">
        <h3 class="editable">初步判断</h3>
        <ul class="editable">
            <li>结合多节点相似现象、底层识别结果及RAID侧表现，当前证据指向RAID控制器固件或驱动与现网操作系统版本兼容性不足的可能性较高，建议结合硬件厂商进一步完成版本适配核验。</li>
        </ul>
    </div>
    
    <div class="analysis-section" style="background-color: #e8f5e9;">
        <h3 class="editable">排除因素</h3>
        <ul class="editable">
            <li>✓ 存储平台当时没有大流量出现，排除存储性能问题</li>
            <li>✓ 云平台虚拟机监控显示CPU和磁盘负载均不高，排除资源过载问题</li>
            <li>✓ 非系统性故障，而是局部硬件和配置问题</li>
        </ul>
    </div>
</div>
```

#### 6. 处置与治理方案
```html
<div class="content-section">
    <div class="section-header editable">三、处置与治理方案</div>
    
    <div class="timeline-section">
        <div class="timeline-item">
            <h4 class="editable"><span class="phase-badge">临时</span>临时处置方案（建议在维护窗口内执行）</h4>
            <ul class="editable">
                <li>建议对 compute-node-01 和 compute-node-02 节点安排重启验证，以确认磁盘识别异常是否可在系统重载后恢复。</li>
                <li>建议对 compute-node-03 节点执行 OSD 数据库残留清理及一致性复核，避免历史残留信息继续影响当前状态判断。</li>
                <li>建议尽快更换 backup-node-01 的故障磁盘，并在更换完成后核验 RAID 组状态与数据同步情况。</li>
            </ul>
        </div>
        
        <div class="timeline-item">
            <h4 class="editable"><span class="phase-badge">长期</span>长期治理方案</h4>
            <ul class="editable">
                <li>建议联合硬件厂商对相关节点RAID控制器固件、驱动与当前操作系统版本的兼容性进行专项核查，并形成升级计划。</li>
                <li>建议对现网节点RAID配置、磁盘健康状态及固件版本开展一次专项巡检，提前识别同类隐患。</li>
                <li>建议补充磁盘与控制器健康监控、告警与巡检机制，完善硬件异常场景下的标准处置预案。</li>
                <li>建议建立定期固件评估与升级机制，并同步完善运维侧巡检清单与故障复盘流程。</li>
            </ul>
        </div>
    </div>
</div>
```

## 示例2：简化的markdown输入

### 输入
```markdown
客户：某客户
时间：2026-06-16
版本：ZStack 4.4

故障：虚拟机无法启动

节点 node-01:
- OSD osd.5 offline
- 磁盘sdb故障

排查结论：当前已确认磁盘 sdb 存在故障表现，建议在维护窗口内安排硬件更换并完成状态复核。
```

### 处理策略
对于这种简化格式：
1. **提取可用信息**：客户名、时间、版本、故障描述
2. **推断缺失信息**：
   - 故障影响：根据"虚拟机无法启动"推断
   - 故障级别：默认为"三级（一般）"
   - 报告人：留空让用户填写
3. **生成基础结构**：至少包含一个node-detail块
4. **保留占位符**：对于markdown中未提供的信息，保留`[请填写...]`占位符

## 常见场景处理

### 场景1：多个图片URL连续出现
```markdown
![图1](URL1)
![图2](URL2)
![图3](URL3)
```
→ 使用`image-grid`布局，前两个并排，第三个单独一行或继续并排（取决于数量）

### 场景2：节点信息不完整
```markdown
### 节点 compute-node-01
问题：磁盘故障
```
→ 生成node-detail时，缺失的字段（如SN号、OSD）留空或使用占位符

### 场景3：markdown中有表格
```markdown
| 节点 | OSD | 状态 |
|------|-----|------|
| node-01 | osd.5 | offline |
```
→ 转换为HTML表格或转换为列表形式放入detail-item中

### 场景4：markdown中包含代码块
```markdown
```bash
lsblk
fdisk -l
```
→ 可以忽略，或在report中添加添加一个"相关命令"section

## 输出质量检查

生成HTML后，必须验证：
1. ✅ 所有图片URL都已正确嵌入
2. ✅ 节点编号从1开始连续递增
3. ✅ 每个节点都有recommendation-box
4. ✅ 基本信息表至少有客户名、时间、版本
5. ✅ 故障现象有highlight-box突出显示
6. ✅ JavaScript编辑功能完整
7. ✅ CSS打印样式完整
8. ✅ 文件保存在Downloads目录

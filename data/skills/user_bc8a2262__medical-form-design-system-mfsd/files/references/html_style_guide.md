# HTML表单样式规范指南

本文档定义医疗表单 HTML 输出的样式规范，AI 生成 HTML 表单时必须遵循以下规范。

---

## 基础 HTML 结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>表单标题</title>
  <style>
    /* 内联样式 - 参见下方CSS规范 */
  </style>
</head>
<body>
  <div class="form-container">
    <div class="form-header">
      <h2 class="form-title">表单名称</h2>
      <p class="form-desc">表单说明文字（来源文件名/版本）</p>
    </div>
    <form id="medical-form" onsubmit="handleSubmit(event)">
      <!-- 字段分组 -->
      <fieldset class="form-section">
        <legend class="section-title">基本信息</legend>
        <!-- 字段循环 -->
      </fieldset>
      <!-- 提交区 -->
      <div class="form-actions">
        <button type="submit" class="btn-primary">提交</button>
        <button type="reset" class="btn-secondary">重置</button>
      </div>
    </form>
  </div>
</body>
</html>
```

---

## CSS 样式规范

```css
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
  font-size: 14px;
  color: #333;
  background: #f5f7fa;
  padding: 20px;
}

.form-container {
  max-width: 860px;
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  overflow: hidden;
}

.form-header {
  background: linear-gradient(135deg, #1a6fc4 0%, #2196F3 100%);
  color: #fff;
  padding: 24px 32px;
}

.form-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 6px;
}

.form-desc {
  font-size: 13px;
  opacity: 0.85;
}

form {
  padding: 24px 32px;
}

fieldset.form-section {
  border: 1px solid #e4e8f0;
  border-radius: 6px;
  padding: 16px 20px;
  margin-bottom: 20px;
  background: #fafbfc;
}

legend.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a6fc4;
  padding: 0 8px;
  background: #fff;
  border: 1px solid #c7d8f0;
  border-radius: 4px;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 14px;
}

.form-group {
  flex: 1 1 280px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group.full-width {
  flex: 1 1 100%;
}

label {
  font-size: 13px;
  color: #555;
  font-weight: 500;
}

label .required {
  color: #e53935;
  margin-left: 2px;
}

input[type="text"],
input[type="number"],
input[type="date"],
input[type="email"],
input[type="tel"],
select,
textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d0d7e3;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: #fff;
  transition: border-color 0.2s;
  font-family: inherit;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33,150,243,0.15);
}

textarea {
  min-height: 80px;
  resize: vertical;
}

select[multiple] {
  min-height: 100px;
}

/* 单选/复选框组 */
.radio-group, .checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 4px;
}

.radio-item, .checkbox-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  cursor: pointer;
}

.radio-item input, .checkbox-item input {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #2196F3;
}

/* 矩阵表 */
.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-top: 8px;
}

.matrix-table th {
  background: #e3edf8;
  color: #1a6fc4;
  padding: 8px 10px;
  border: 1px solid #c7d8f0;
  text-align: center;
  font-weight: 600;
}

.matrix-table td {
  padding: 6px 8px;
  border: 1px solid #e0e7ef;
  vertical-align: middle;
}

.matrix-table tr:nth-child(even) {
  background: #f5f8fc;
}

.matrix-table td input,
.matrix-table td select {
  width: 100%;
  padding: 4px 6px;
  border: 1px solid #d0d7e3;
  border-radius: 3px;
  font-size: 13px;
}

/* 文件上传 */
.file-upload-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

input[type="file"] {
  font-size: 13px;
  padding: 6px;
  border: 1px dashed #90b8e0;
  border-radius: 4px;
  background: #f0f7ff;
  color: #555;
  cursor: pointer;
}

.file-hint {
  font-size: 12px;
  color: #999;
}

/* 提交区 */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px 0 8px;
  border-top: 1px solid #edf0f5;
  margin-top: 10px;
}

.btn-primary {
  padding: 10px 36px;
  background: linear-gradient(135deg, #1a6fc4, #2196F3);
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 15px;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(33,150,243,0.35);
  transition: opacity 0.2s;
}

.btn-primary:hover { opacity: 0.88; }

.btn-secondary {
  padding: 10px 36px;
  background: #fff;
  color: #666;
  border: 1px solid #d0d7e3;
  border-radius: 20px;
  font-size: 15px;
  cursor: pointer;
  font-weight: 500;
  transition: border-color 0.2s;
}

.btn-secondary:hover { border-color: #2196F3; color: #2196F3; }
```

---

## 控件代码片段参考

### text — 单行文本
```html
<div class="form-group">
  <label for="patient_name">患者姓名<span class="required">*</span></label>
  <input type="text" id="patient_name" name="patient_name" placeholder="请输入患者姓名" required>
</div>
```

### textarea — 长文本
```html
<div class="form-group full-width">
  <label for="diagnosis_desc">诊断描述</label>
  <textarea id="diagnosis_desc" name="diagnosis_desc" placeholder="请输入详细诊断描述" rows="4"></textarea>
</div>
```

### select — 下拉选择（来自用户截图）
```html
<div class="form-group">
  <label for="gender">性别<span class="required">*</span></label>
  <select id="gender" name="gender" required>
    <option value="">请选择</option>
    <option value="男">男</option>
    <option value="女">女</option>
  </select>
</div>
```

> 注：参照用户提供的HTML代码样式示例，input使用placeholder属性，select使用option子元素

### radio — 单选按钮组
```html
<div class="form-group">
  <label>分级<span class="required">*</span></label>
  <div class="radio-group">
    <label class="radio-item"><input type="radio" name="grade" value="轻度"> 轻度</label>
    <label class="radio-item"><input type="radio" name="grade" value="中度"> 中度</label>
    <label class="radio-item"><input type="radio" name="grade" value="重度"> 重度</label>
  </div>
</div>
```

### checkbox — 多选框组
```html
<div class="form-group full-width">
  <label>并发症（可多选）</label>
  <div class="checkbox-group">
    <label class="checkbox-item"><input type="checkbox" name="complication" value="高血压"> 高血压</label>
    <label class="checkbox-item"><input type="checkbox" name="complication" value="糖尿病"> 糖尿病</label>
    <label class="checkbox-item"><input type="checkbox" name="complication" value="肾病"> 肾病</label>
  </div>
</div>
```

### date — 日期选择
```html
<div class="form-group">
  <label for="visit_date">就诊日期<span class="required">*</span></label>
  <input type="date" id="visit_date" name="visit_date" placeholder="yyyy-mm-dd" required>
</div>
```

### number — 数字输入
```html
<div class="form-group">
  <label for="age">年龄（岁）</label>
  <input type="number" id="age" name="age" min="0" max="150" placeholder="请输入年龄">
</div>
```

### file — 附件上传
```html
<div class="form-group full-width">
  <label>检查报告（附件）</label>
  <div class="file-upload-wrapper">
    <input type="file" name="report_file" accept=".pdf,.jpg,.png,.docx">
    <span class="file-hint">支持PDF/图片/Word，单个文件不超过10MB</span>
  </div>
</div>
```

### matrix — 矩阵表格
```html
<div class="form-group full-width">
  <label>检验检查结果</label>
  <table class="matrix-table">
    <thead>
      <tr>
        <th>检查项目</th>
        <th>检查日期</th>
        <th>检查结果</th>
        <th>参考范围</th>
        <th>是否异常</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="text" placeholder="项目名称"></td>
        <td><input type="date"></td>
        <td><input type="text" placeholder="结果值+单位"></td>
        <td><input type="text" placeholder="参考范围"></td>
        <td>
          <select>
            <option value="">请选择</option>
            <option value="否">否</option>
            <option value="是">是</option>
          </select>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

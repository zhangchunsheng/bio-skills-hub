# XML表单模板规范

本文档定义医疗表单 XML 输出结构，兼容 HIS/EMR 系统导入格式。

---

## XML 根结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MedicalForm xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             version="1.0"
             createDate="生成日期">

  <!-- 表单元信息 -->
  <FormMeta>
    <FormName>表单名称</FormName>
    <FormCode>FORM_001</FormCode>
    <BusinessType>CLN|MGT|RES</BusinessType>
    <GenreType>GUIDE|SOP|POLICY|...</GenreType>
    <SourceDocument>来源文件名</SourceDocument>
    <Version>1.0</Version>
    <CreateTime>2026-01-01T00:00:00</CreateTime>
  </FormMeta>

  <!-- 字段分组 -->
  <FormSections>
    <Section id="section_001" name="基本信息" order="1">
      <Fields>
        <Field id="field_001" order="1">
          <Label>患者姓名</Label>
          <FieldCode>patient_name</FieldCode>
          <ControlType>text</ControlType>
          <DataType>string</DataType>
          <Required>true</Required>
          <Placeholder>请输入患者姓名</Placeholder>
          <MaxLength>50</MaxLength>
          <DefaultValue></DefaultValue>
          <Hint></Hint>
          <Options/>
          <Validation>
            <Rule>notEmpty</Rule>
            <Message>患者姓名不能为空</Message>
          </Validation>
        </Field>

        <Field id="field_002" order="2">
          <Label>性别</Label>
          <FieldCode>gender</FieldCode>
          <ControlType>select</ControlType>
          <DataType>string</DataType>
          <Required>true</Required>
          <Placeholder>请选择</Placeholder>
          <Options>
            <Option value="男">男</Option>
            <Option value="女">女</Option>
          </Options>
        </Field>

        <Field id="field_003" order="3">
          <Label>就诊日期</Label>
          <FieldCode>visit_date</FieldCode>
          <ControlType>date</ControlType>
          <DataType>date</DataType>
          <Required>true</Required>
          <Placeholder>yyyy-mm-dd</Placeholder>
          <DateFormat>YYYY-MM-DD</DateFormat>
        </Field>
      </Fields>
    </Section>
  </FormSections>

</MedicalForm>
```

---

## 控件类型与DataType映射

| ControlType | DataType | 说明 |
|-------------|----------|------|
| text | string | 单行文本 |
| textarea | string | 多行长文本 |
| number | decimal/integer | 数字 |
| date | date | 日期 yyyy-mm-dd |
| select | string | 下拉单选 |
| radio | string | 单选按钮 |
| checkbox | array | 多选框，值用逗号分隔 |
| multiselect | array | 多选下拉 |
| file | binary | 附件 |
| matrix | array | 矩阵表，值为JSON数组 |

---

## 矩阵字段 XML 示例

```xml
<Field id="field_matrix_001" order="10">
  <Label>检验检查结果</Label>
  <FieldCode>lab_results</FieldCode>
  <ControlType>matrix</ControlType>
  <DataType>array</DataType>
  <Required>false</Required>
  <MatrixColumns>
    <Column id="col_1" type="text" label="检查项目"/>
    <Column id="col_2" type="date" label="检查日期"/>
    <Column id="col_3" type="text" label="检查结果"/>
    <Column id="col_4" type="text" label="参考范围"/>
    <Column id="col_5" type="select" label="是否异常">
      <Options>
        <Option value="否">否</Option>
        <Option value="是">是</Option>
      </Options>
    </Column>
  </MatrixColumns>
  <InitialRows>3</InitialRows>
</Field>
```

# SCSS样式预处理

## 什么是SCSS/Sass？

SCSS（Sassy CSS）是CSS的预处理器，它为CSS添加了变量、嵌套、混合、函数等编程特性，让样式编写更加高效和可维护。

**英文原意**：Sassy CSS（时髦的CSS）
**中文理解**：CSS的"增强版"，给CSS加上了编程语言的能力

**生活类比**：就像用高级语言（如JavaScript）代替机器语言编写程序，SCSS让我们用更高级的方式编写CSS，然后编译成浏览器能识别的普通CSS。

### Sass vs SCSS的区别

| 特性 | Sass | SCSS |
|------|------|------|
| 文件扩展名 | `.sass` | `.scss` |
| 语法风格 | 缩进式（类似Python） | 大括号式（类似CSS） |
| 分号 | 不需要 | 需要 |
| 大括号 | 不需要 | 需要 |
| 兼容性 | 与CSS差异较大 | 完全兼容CSS |

```scss
// Sass语法（缩进式）
$primary-color: #333

body
  color: $primary-color
  font-size: 14px

// SCSS语法（大括号式）
$primary-color: #333;

body {
  color: $primary-color;
  font-size: 14px;
}
```

**LiuMa项目使用的是SCSS语法**，因为它与CSS完全兼容，学习成本低。

## 为什么选择SCSS？

### 1. CSS预处理器对比

| 预处理器 | 特点 | 优点 | 缺点 |
|----------|------|------|------|
| **SCSS/Sass** | 功能最全面 | 功能强大、生态成熟 | 学习成本稍高 |
| Less | 类似CSS的语法 | 学习简单、与Bootstrap集成好 | 功能相对较少 |
| Stylus | 语法最灵活 | 语法自由、功能强大 | 社区相对较小 |
| PostCSS | 后处理器 | 插件化、现代化 | 需要配置多个插件 |

### 2. SCSS的核心优势

- **变量系统**：统一管理颜色、字体、间距等
- **嵌套语法**：层级结构清晰，避免重复书写
- **混合（Mixin）**：复用样式代码块
- **继承（Extend）**：减少重复代码
- **函数**：强大的内置函数和自定义函数
- **模块化**：支持文件导入和局部作用域

## 核心概念详解

### 1. 变量（Variables）

**英文原意**：变量
**技术含义**：存储可重用的值，如颜色、字体大小、间距等

```scss
// 定义变量
$primary-color: #409EFF;        // 主色调
$success-color: #67C23A;        // 成功色
$warning-color: #E6A23C;        // 警告色
$danger-color: #F56C6C;        // 危险色
$info-color: #909399;           // 信息色

$font-size-base: 14px;          // 基础字体大小
$font-size-large: 16px;         // 大字体
$font-size-small: 12px;         // 小字体

$spacing-base: 20px;            // 基础间距
$spacing-small: 10px;           // 小间距
$spacing-large: 30px;             // 大间距

// 使用变量
.button {
  background-color: $primary-color;
  font-size: $font-size-base;
  padding: $spacing-small $spacing-base;
}

.card {
  margin-bottom: $spacing-base;
  font-size: $font-size-large;
}
```

### 2. 嵌套（Nesting）

**英文原意**：嵌套
**技术含义**：在样式规则内部嵌套其他规则，反映HTML的层级结构

```scss
// 传统CSS写法
.card {}
.card .card-header {}
.card .card-header .card-title {}
.card .card-body {}
.card .card-footer {}

// SCSS嵌套写法
.card {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  
  .card-header {
    padding: 18px 20px;
    border-bottom: 1px solid #e4e7ed;
    
    .card-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
  }
  
  .card-body {
    padding: 20px;
  }
  
  .card-footer {
    padding: 10px 20px;
    border-top: 1px solid #e4e7ed;
    background-color: #f5f7fa;
  }
}

// 父选择器引用（&）
.button {
  background: #fff;
  
  &:hover {
    background: #f5f7fa;
  }
  
  &.primary {
    background: #409EFF;
    color: #fff;
  }
  
  &.large {
    padding: 12px 24px;
    font-size: 16px;
  }
}
```

### 3. 混合（Mixin）

**英文原意**：混合、混入
**技术含义**：可重用的样式代码块，可以接收参数

```scss
// 定义混合
@mixin button-base {
  display: inline-block;
  line-height: 1;
  white-space: nowrap;
  cursor: pointer;
  border: 1px solid #dcdfe6;
  text-align: center;
  box-sizing: border-box;
  outline: none;
  margin: 0;
  transition: .1s;
  font-weight: 500;
  user-select: none;
}

// 带参数的混合
@mixin button-size($padding-vertical, $padding-horizontal, $font-size) {
  padding: $padding-vertical $padding-horizontal;
  font-size: $font-size;
  border-radius: 4px;
}

@mixin button-variant($color, $background, $border) {
  color: $color;
  background-color: $background;
  border-color: $border;
  
  &:hover {
    background: lighten($background, 10%);
    border-color: lighten($border, 10%);
  }
  
  &:active {
    background: darken($background, 10%);
    border-color: darken($border, 10%);
  }
}

// 使用混合
.button {
  @include button-base;
  
  &.default {
    @include button-variant(#606266, #fff, #dcdfe6);
  }
  
  &.primary {
    @include button-variant(#fff, #409EFF, #409EFF);
  }
  
  &.small {
    @include button-size(9px, 15px, 12px);
  }
  
  &.medium {
    @include button-size(10px, 20px, 14px);
  }
  
  &.large {
    @include button-size(12px, 24px, 16px);
  }
}
```

### 4. 继承（Extend）

**英文原意**：扩展、继承
**技术含义**：让一个选择器继承另一个选择器的样式

```scss
// 基础样式
%message-base {
  padding: 10px 15px;
  margin-bottom: 20px;
  border: 1px solid transparent;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
}

// 继承基础样式
.message {
  @extend %message-base;
  color: #606266;
  background-color: #f4f4f5;
  border-color: #e4e7ed;
}

.message-success {
  @extend %message-base;
  color: #67c23a;
  background-color: #f0f9ff;
  border-color: #c2e7b0;
}

.message-warning {
  @extend %message-base;
  color: #e6a23c;
  background-color: #fdf6ec;
  border-color: #f5dab1;
}

.message-error {
  @extend %message-base;
  color: #f56c6c;
  background-color: #fef0f0;
  border-color: #fbc4c4;
}
```

### 5. 函数（Functions）

**英文原意**：函数
**技术含义**：SCSS提供的内置函数和自定义函数

```scss
// 颜色函数
$primary: #409EFF;

.button {
  background: $primary;
  
  &:hover {
    background: lighten($primary, 10%); // 变亮10%
  }
  
  &:active {
    background: darken($primary, 10%); // 变暗10%
  }
  
  &.disabled {
    background: desaturate($primary, 50%); // 降低饱和度
    opacity: 0.6;
  }
}

// 数学函数
.sidebar {
  width: percentage(1/3); // 转换为百分比
  font-size: round(14.6px); // 四舍五入
  margin: abs(-10px); // 绝对值
}

// 字符串函数
$font-family: 'Helvetica Neue';

.body {
  font-family: quote($font-family); // 添加引号
  font-size: str-length('Hello World'); // 字符串长度
}

// 自定义函数
@function calculate-rem($pixels, $base-font-size: 16px) {
  @return $pixels / $base-font-size * 1rem;
}

.title {
  font-size: calculate-rem(24px); // 计算rem值
}
```

### 6. 导入（Import）

**英文原意**：导入
**技术含义**：将多个SCSS文件合并在一起

```scss
// _variables.scss - 变量定义
$primary-color: #409EFF;
$success-color: #67C23A;
$warning-color: #E6A23C;
$danger-color: #F56C6C;

// _mixins.scss - 混合定义
@mixin button-variant($color, $background) {
  color: $color;
  background-color: $background;
  
  &:hover {
    background: darken($background, 10%);
  }
}

// _base.scss - 基础样式
body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', SimSun, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  color: #303133;
  background-color: #fff;
}

// main.scss - 主样式文件
@import 'variables';
@import 'mixins';
@import 'base';

.button {
  @include button-variant(#fff, $primary-color);
}
```

## 在LiuMa项目中的应用

### 1. 项目样式结构

```
src/
├── assets/
│   ├── styles/           # 样式文件目录
│   │   ├── variables.scss    # 全局变量
│   │   ├── mixins.scss       # 全局混合
│   │   ├── common.scss       # 公共样式
│   │   └── element-ui.scss   # Element UI自定义
│   └── index.js         # 样式入口文件
```

### 2. 全局变量定义（/src/assets/styles/variables.scss）

```scss
// 颜色变量
$color-primary: #409EFF;
$color-success: #67C23A;
$color-warning: #E6A23C;
$color-danger: #F56C6C;
$color-info: #909399;

$color-white: #FFFFFF;
$color-black: #000000;
$color-grey: #C0C4CC;

// 文字颜色
$color-text-primary: #303133;
$color-text-regular: #606266;
$color-text-secondary: #909399;
$color-text-placeholder: #C0C4CC;

// 边框颜色
$border-color-base: #DCDFE6;
$border-color-light: #E4E7ED;
$border-color-lighter: #EBEEF5;
$border-color-extra-light: #F2F6FC;

// 背景颜色
$bg-color-base: #F5F7FA;
$bg-color-light: #FAFAFA;
$bg-color-lighter: #FDFDFD;

// 字体大小
$font-size-base: 14px;
$font-size-large: 16px;
$font-size-small: 12px;
$font-size-mini: 10px;

// 间距
$spacing-base: 20px;
$spacing-small: 10px;
$spacing-large: 30px;
$spacing-extra-large: 40px;

// 边框圆角
$border-radius-base: 4px;
$border-radius-small: 2px;
$border-radius-large: 6px;

// 阴影
$box-shadow-base: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04);
$box-shadow-light: 0 2px 12px 0 rgba(0, 0, 0, .1);

// 过渡动画
$transition-base: all .3s cubic-bezier(.645,.045,.355,1);
$transition-fast: all .2s cubic-bezier(.645,.045,.355,1);
$transition-slow: all .5s cubic-bezier(.645,.045,.355,1);
```

### 3. 全局混合定义（/src/assets/styles/mixins.scss）

```scss
// 清除浮动
@mixin clearfix {
  &:before,
  &:after {
    content: "";
    display: table;
  }
  
  &:after {
    clear: both;
  }
}

// 文字省略
@mixin ellipsis {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

// 多行文字省略
@mixin ellipsis-multiline($lines: 2) {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: $lines;
  overflow: hidden;
}

// 按钮基础样式
@mixin button-base {
  display: inline-block;
  line-height: 1;
  white-space: nowrap;
  cursor: pointer;
  background: $color-white;
  border: 1px solid $border-color-base;
  color: $color-text-regular;
  -webkit-appearance: none;
  text-align: center;
  box-sizing: border-box;
  outline: none;
  margin: 0;
  transition: $transition-base;
  font-weight: 500;
  user-select: none;
  
  &:hover {
    color: $color-primary;
    border-color: lighten($color-primary, 20%);
    background-color: lighten($color-primary, 45%);
  }
  
  &:active {
    color: darken($color-primary, 10%);
    border-color: darken($color-primary, 10%);
  }
}

// 按钮尺寸
@mixin button-size($padding-vertical, $padding-horizontal, $font-size, $border-radius) {
  padding: $padding-vertical $padding-horizontal;
  font-size: $font-size;
  border-radius: $border-radius;
}

// 按钮类型
@mixin button-variant($color, $background, $border) {
  color: $color;
  background-color: $background;
  border-color: $border;
  
  &:hover {
    background: lighten($background, 10%);
    border-color: lighten($border, 10%);
    color: $color;
  }
  
  &:active {
    background: darken($background, 10%);
    border-color: darken($border, 10%);
    color: $color;
  }
}

// 卡片阴影
@mixin card-shadow($level: 1) {
  @if $level == 1 {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  } @else if $level == 2 {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  } @else if $level == 3 {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
}

// 响应式断点
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'mobile' {
    @media (max-width: 768px) {
      @content;
    }
  } @else if $breakpoint == 'tablet' {
    @media (max-width: 1024px) {
      @content;
    }
  } @else if $breakpoint == 'desktop' {
    @media (min-width: 1025px) {
      @content;
    }
  }
}
```

### 4. 组件样式示例

```scss
// 自定义按钮组件样式
.custom-button {
  @include button-base;
  @include button-size(10px, 20px, 14px, $border-radius-base);
  
  &.primary {
    @include button-variant($color-white, $color-primary, $color-primary);
  }
  
  &.success {
    @include button-variant($color-white, $color-success, $color-success);
  }
  
  &.warning {
    @include button-variant($color-white, $color-warning, $color-warning);
  }
  
  &.large {
    @include button-size(12px, 24px, 16px, $border-radius-base);
  }
  
  &.small {
    @include button-size(7px, 15px, 12px, $border-radius-small);
  }
}

// 卡片组件样式
.custom-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-base;
  background: $color-white;
  @include card-shadow(1);
  
  .card-header {
    padding: $spacing-base;
    border-bottom: 1px solid $border-color-lighter;
    
    .card-title {
      font-size: $font-size-large;
      font-weight: 500;
      color: $color-text-primary;
      margin: 0;
    }
  }
  
  .card-body {
    padding: $spacing-base;
  }
  
  .card-footer {
    padding: $spacing-small $spacing-base;
    border-top: 1px solid $border-color-lighter;
    background: $bg-color-base;
  }
}

// 表格样式
.custom-table {
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: $spacing-small $spacing-base;
    text-align: left;
    border-bottom: 1px solid $border-color-lighter;
  }
  
  th {
    background: $bg-color-base;
    font-weight: 500;
    color: $color-text-primary;
  }
  
  tbody tr:hover {
    background: $bg-color-base;
  }
  
  @include respond-to('mobile') {
    font-size: $font-size-small;
    
    th, td {
      padding: 8px;
    }
  }
}
```

### 5. Element UI样式覆盖

```scss
// 覆盖Element UI默认样式
// src/assets/styles/element-ui.scss

// 覆盖按钮样式
.el-button {
  border-radius: $border-radius-base;
  transition: $transition-base;
  
  &.el-button--primary {
    background-color: $color-primary;
    border-color: $color-primary;
    
    &:hover {
      background: lighten($color-primary, 10%);
      border-color: lighten($color-primary, 10%);
    }
    
    &:active {
      background: darken($color-primary, 10%);
      border-color: darken($color-primary, 10%);
    }
  }
}

// 覆盖输入框样式
.el-input__inner {
  border-radius: $border-radius-base;
  border-color: $border-color-base;
  
  &:focus {
    border-color: $color-primary;
    box-shadow: 0 0 0 2px rgba($color-primary, 0.2);
  }
}

// 覆盖表格样式
.el-table {
  th {
    background-color: $bg-color-base;
    color: $color-text-primary;
    font-weight: 500;
  }
  
  tr:hover td {
    background-color: lighten($bg-color-base, 2%);
  }
}

// 覆盖卡片样式
.el-card {
  border-radius: $border-radius-base;
  box-shadow: $box-shadow-base;
  
  .el-card__header {
    padding: $spacing-base;
    border-bottom: 1px solid $border-color-lighter;
  }
  
  .el-card__body {
    padding: $spacing-base;
  }
}
```

## 高级特性

### 1. 条件语句

```scss
// 根据主题设置不同样式
$theme: 'light'; // 'light' 或 'dark'

.button {
  @if $theme == 'light' {
    background: $color-white;
    color: $color-text-primary;
    border: 1px solid $border-color-base;
  } @else if $theme == 'dark' {
    background: #2c3e50;
    color: $color-white;
    border: 1px solid #34495e;
  }
}

// 根据屏幕尺寸设置不同样式
$screen-size: 'mobile';

.container {
  @if $screen-size == 'mobile' {
    padding: 10px;
    font-size: 14px;
  } @else {
    padding: 20px;
    font-size: 16px;
  }
}
```

### 2. 循环语句

```scss
// 生成不同尺寸的间距类
@for $i from 1 through 5 {
  .m-#{$i} {
    margin: $i * 4px;
  }
  
  .p-#{$i} {
    padding: $i * 4px;
  }
  
  .mt-#{$i} {
    margin-top: $i * 4px;
  }
  
  .mb-#{$i} {
    margin-bottom: $i * 4px;
  }
}

// 生成不同颜色的按钮
$button-types: (
  'primary': $color-primary,
  'success': $color-success,
  'warning': $color-warning,
  'danger': $color-danger,
  'info': $color-info
);

@each $name, $color in $button-types {
  .button-#{$name} {
    background-color: $color;
    border-color: $color;
    color: $color-white;
    
    &:hover {
      background-color: lighten($color, 10%);
      border-color: lighten($color, 10%);
    }
  }
}

// 生成栅格系统
@for $i from 1 through 12 {
  .col-#{$i} {
    width: percentage($i / 12);
  }
}
```

### 3. 函数

```scss
// 计算rem值
@function rem($pixels, $base-font-size: 16px) {
  @return $pixels / $base-font-size * 1rem;
}

.title {
  font-size: rem(24px); // 输出: 1.5rem
}

// 计算对比度
@function contrast-color($color) {
  $red: red($color);
  $green: green($color);
  $blue: blue($color);
  
  $yiq: (($red * 299) + ($green * 587) + ($blue * 114)) / 1000;
  
  @if ($yiq >= 128) {
    @return #000000; // 亮色背景，使用黑色文字
  } @else {
    @return #ffffff; // 暗色背景，使用白色文字
  }
}

.button {
  $bg-color: #3498db;
  background-color: $bg-color;
  color: contrast-color($bg-color);
}

// 生成z-index层级
@function z-index($layer) {
  $z-indexes: (
    'modal': 2000,
    'dropdown': 1000,
    'header': 100,
    'footer': 50,
    'default': 1
  );
  
  @return map-get($z-indexes, $layer);
}

.modal {
  z-index: z-index('modal');
}
```

## 实战：完整的样式系统

```scss
// 1. 变量定义（_variables.scss）
// 颜色系统
$colors: (
  'primary': #409EFF,
  'success': #67C23A,
  'warning': #E6A23C,
  'danger': #F56C6C,
  'info': #909399,
  'white': #FFFFFF,
  'black': #000000
);

// 字体系统
$font-sizes: (
  'xs': 10px,
  'sm': 12px,
  'base': 14px,
  'lg': 16px,
  'xl': 18px,
  '2xl': 20px,
  '3xl': 24px
);

// 间距系统
$spacings: (
  'xs': 4px,
  'sm': 8px,
  'base': 16px,
  'lg': 24px,
  'xl': 32px,
  '2xl': 48px,
  '3xl': 64px
);

// 2. 工具函数（_functions.scss）
@function color($name) {
  @return map-get($colors, $name);
}

@function font-size($name) {
  @return map-get($font-sizes, $name);
}

@function spacing($name) {
  @return map-get($spacings, $name);
}

// 3. 混合定义（_mixins.scss）
@mixin button-variant($color, $background, $border) {
  color: $color;
  background-color: $background;
  border-color: $border;
  
  &:hover {
    background: lighten($background, 10%);
    border-color: lighten($border, 10%);
  }
  
  &:active {
    background: darken($background, 10%);
    border-color: darken($border, 10%);
  }
}

@mixin button-size($padding-y, $padding-x, $font-size, $border-radius) {
  padding: $padding-y $padding-x;
  font-size: $font-size;
  border-radius: $border-radius;
}

// 4. 基础样式（_base.scss）
* {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: font-size('base');
  line-height: 1.5;
  color: #333;
  margin: 0;
  padding: 0;
}

// 5. 组件样式（_components.scss）
.btn {
  display: inline-block;
  font-weight: 400;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  text-decoration: none;
  
  // 按钮大小
  &.btn-sm {
    @include button-size(spacing('xs'), spacing('sm'), font-size('sm'), 3px);
  }
  
  &.btn-md {
    @include button-size(spacing('sm'), spacing('base'), font-size('base'), 4px);
  }
  
  &.btn-lg {
    @include button-size(spacing('base'), spacing('lg'), font-size('lg'), 6px);
  }
  
  // 按钮颜色
  &.btn-primary {
    @include button-variant(color('white'), color('primary'), color('primary'));
  }
  
  &.btn-success {
    @include button-variant(color('white'), color('success'), color('success'));
  }
  
  &.btn-warning {
    @include button-variant(color('white'), color('warning'), color('warning'));
  }
  
  &.btn-danger {
    @include button-variant(color('white'), color('danger'), color('danger'));
  }
}

.card {
  background: color('white');
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  
  .card-header {
    padding: spacing('base');
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;
    
    .card-title {
      margin: 0;
      font-size: font-size('lg');
      font-weight: 500;
    }
  }
  
  .card-body {
    padding: spacing('base');
  }
  
  .card-footer {
    padding: spacing('sm') spacing('base');
    border-top: 1px solid #e0e0e0;
    background: #f8f9fa;
  }
}

// 6. 工具类（_utilities.scss）
// 文字对齐
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

// 文字颜色
@each $name, $value in $colors {
  .text-#{$name} {
    color: $value;
  }
}

// 背景颜色
@each $name, $value in $colors {
  .bg-#{$name} {
    background-color: $value;
  }
}

// 间距类
@each $name, $value in $spacings {
  .m-#{$name} { margin: $value; }
  .mt-#{$name} { margin-top: $value; }
  .mb-#{$name} { margin-bottom: $value; }
  .ml-#{$name} { margin-left: $value; }
  .mr-#{$name} { margin-right: $value; }
  .p-#{$name} { padding: $value; }
  .pt-#{$name} { padding-top: $value; }
  .pb-#{$name} { padding-bottom: $value; }
  .pl-#{$name} { padding-left: $value; }
  .pr-#{$name} { padding-right: $value; }
}

// 7. 主样式文件（main.scss）
@import 'variables';
@import 'functions';
@import 'mixins';
@import 'base';
@import 'components';
@import 'utilities';
```

## 性能优化技巧

### 1. 减少编译时间

```scss
// 使用局部导入，只导入需要的文件
@import 'components/button';
@import 'components/card';
@import 'components/table';

// 避免深层嵌套（不超过3层）
.card {
  .card-header {
    .card-title {
      // 最多3层嵌套
      color: $primary;
    }
  }
}

// 使用变量代替重复计算
$button-padding: 10px 20px;

.button {
  padding: $button-padding; // 使用变量
}
```

### 2. 减少输出文件大小

```scss
// 使用占位符选择器（%）而不是类选择器（.）
%button-base {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
}

.button-primary {
  @extend %button-base;
  background: $primary;
}

.button-secondary {
  @extend %button-base;
  background: $secondary;
}

// 避免生成重复的CSS
// 不好的做法
.button-primary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background: $primary;
}

.button-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background: $secondary;
}
```

### 3. 使用PostCSS优化

```javascript
// postcss.config.js
module.exports = {
  plugins: [
    require('autoprefixer')({
      overrideBrowserslist: ['last 2 versions', 'ie >= 11']
    }),
    require('cssnano')({
      preset: 'default',
    }),
  ],
}
```

## 常见问题解答

### Q1：SCSS和CSS有什么区别？

**A**：
- **CSS**：层叠样式表，浏览器直接识别的基础样式语言
- **SCSS**：CSS的预处理器，添加了变量、嵌套、混合等编程特性，需要编译成CSS才能被浏览器识别

**类比**：CSS像手动挡汽车，SCSS像自动挡汽车，SCSS让驾驶（写样式）变得更简单。

### Q2：如何在Vue项目中使用SCSS？

**A**：
1. 安装依赖：`npm install sass-loader node-sass -D`
2. 在组件中使用：`<style lang="scss">`
3. 配置全局变量：在`vue.config.js`中配置

```javascript
// vue.config.js
module.exports = {
  css: {
    loaderOptions: {
      sass: {
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  }
}
```

### Q3：SCSS文件命名有什么规范？

**A**：
- **下划线前缀**：`_variables.scss`表示局部文件，不会单独编译
- **主文件**：`main.scss`或`index.scss`作为入口文件
- **模块化**：按功能模块命名，如`_button.scss`、`_card.scss`

### Q4：如何处理SCSS的浏览器兼容性问题？

**A**：
1. 使用PostCSS的autoprefixer自动添加浏览器前缀
2. 避免使用实验性的CSS特性
3. 使用Can I Use网站检查兼容性

### Q5：SCSS编译报错如何调试？

**A**：
1. 检查变量是否定义
2. 检查混合和函数的参数
3. 检查嵌套层级是否过深
4. 使用Source Map定位错误位置

## 实战：从零搭建SCSS样式系统

```scss
// 1. 创建项目结构
styles/
├── abstracts/        # 抽象层（变量、函数、混合）
│   ├── _variables.scss
│   ├── _functions.scss
│   └── _mixins.scss
├── base/            # 基础层（重置、字体、基础样式）
│   ├── _reset.scss
│   ├── _typography.scss
│   └── _base.scss
├── components/      # 组件层（按钮、卡片、表单等）
│   ├── _buttons.scss
│   ├── _cards.scss
│   └── _forms.scss
├── layout/          # 布局层（头部、侧边栏、网格等）
│   ├── _header.scss
│   ├── _sidebar.scss
│   └── _grid.scss
├── pages/           # 页面层（特定页面样式）
│   ├── _home.scss
│   └── _login.scss
├── themes/          # 主题层（不同主题样式）
│   ├── _theme-light.scss
│   └── _theme-dark.scss
├── utilities/       # 工具层（工具类）
│   └── _utilities.scss
└── main.scss        # 主入口文件

// 2. 主文件（main.scss）
@import 'abstracts/variables';
@import 'abstracts/functions';
@import 'abstracts/mixins';

@import 'base/reset';
@import 'base/typography';
@import 'base/base';

@import 'components/buttons';
@import 'components/cards';
@import 'components/forms';

@import 'layout/header';
@import 'layout/sidebar';
@import 'layout/grid';

@import 'utilities/utilities';

// 3. 使用示例
// 在Vue组件中使用
<style lang="scss">
@import '@/assets/styles/main.scss';

.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, color('primary'), color('info'));
  
  .login-card {
    @extend .card;
    width: 100%;
    max-width: 400px;
    
    .login-header {
      text-align: center;
      margin-bottom: spacing('lg');
      
      h2 {
        color: color('primary');
        font-size: font-size('2xl');
        margin: 0;
      }
    }
    
    .login-form {
      .form-group {
        margin-bottom: spacing('base');
        
        label {
          display: block;
          margin-bottom: spacing('xs');
          color: color('text-primary');
          font-weight: 500;
        }
        
        input {
          width: 100%;
          padding: spacing('sm');
          border: 1px solid color('border');
          border-radius: $border-radius-base;
          font-size: font-size('base');
          
          &:focus {
            outline: none;
            border-color: color('primary');
            box-shadow: 0 0 0 3px rgba(color('primary'), 0.1);
          }
        }
      }
      
      .login-button {
        @extend .btn;
        @extend .btn-primary;
        @extend .btn-lg;
        width: 100%;
        margin-top: spacing('base');
      }
    }
  }
}
</style>
```

## 下一步学习

掌握了SCSS基础后，建议继续学习：
1. **CSS Grid和Flexbox** - 现代CSS布局技术
2. **CSS自定义属性（变量）** - 原生CSS变量
3. **PostCSS** - CSS后处理器
4. **Tailwind CSS** - 实用优先的CSS框架
5. **CSS-in-JS** - JavaScript中的CSS

## 面试常见问题

1. **SCSS和Sass有什么区别？**
2. **SCSS中的变量和CSS自定义属性有什么区别？**
3. **Mixin和Extend有什么区别？什么时候用哪个？**
4. **如何在Vue项目中配置SCSS全局变量？**
5. **SCSS编译成CSS的原理是什么？**
6. **如何处理SCSS的浏览器兼容性问题？**
7. **SCSS中的@function和@mixin有什么区别？**
8. **如何优化SCSS的编译性能？**

通过本教程的学习，你应该对SCSS有了全面的了解。LiuMa项目中的样式系统是一个很好的实战案例，建议你仔细研究其变量定义、混合使用和组件样式的实现思路。
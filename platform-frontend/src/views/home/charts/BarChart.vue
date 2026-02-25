/**
 * 柱状图组件（ECharts柱状图，支持外部传入数据与更新）
 */
<template>
    <!-- 图表容器：根据传入id初始化实例，充满父容器 -->
    <div class="echart" :id="id" :style="{float:'left',width: '100%', height: '100%'}"></div> <!-- 承载ECharts实例的div -->
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: "BarChart",
  props: ["id", "title", "data", "name"], // 组件入参：容器id/标题/数据/序列名
  data() {
    return {
      option: {
        // 图表标题配置
        title: {
            text: this.title, // 主标题文本
            subtext: '', // 副标题文本
            left: 'center' // 标题居中
        },
        tooltip: {
          trigger: 'axis', // 触发类型：按轴触发
          axisPointer: {
            label: {
              backgroundColor: '#283b56' // 指示器标签背景
            }
          }
        },
        xAxis: {
          type: 'value', // X轴数值轴
          max: 'dataMax' // 最大值取数据最大值
        },
        yAxis: {
          type: 'category', // Y轴类目轴
          data: this.data.y, // 类目名称列表
          inverse: true, // 倒序显示
          nameTextStyle: {
            width: 600, // 文本宽度
            ellipsis: "..." // 过长省略显示
          }
        },
        series: [{
          name: this.name, // 序列名称
          data: this.data.x, // 序列数据（数值）
          type: 'bar', // 柱状图
        }],
        grid: {
            left: '2%', // 左边距
            right: '5%', // 右边距
            bottom: '5%', // 底边距
            containLabel: true // 包含坐标轴标签
        }
      }
    }
  },
  // 挂载后：初始化图表实例并设置配置项
  mounted() {
    this.myChart = echarts.init(document.getElementById(this.id)); // 初始化图表实例
    this.initChart(); // 设置初始配置
  },
  methods:{
    // 初始化图表：应用配置并绑定自适应
    initChart() {
      this.myChart.setOption(this.option); // 设置初始配置
      // 随屏幕大小调整图表尺寸
      window.addEventListener("resize", () => {
        this.myChart.resize();
      });
    },
    // 更新图表：接收新数据并刷新
    updateChart(data) {
      if (data === null) { return; }
      this.option.yAxis.data = data.y; // 更新类目
      this.option.series[0].data = data.x; // 更新数值
      this.myChart.setOption(this.option); // 应用更新配置
      this.$forceUpdate(); // 强制组件刷新
      // 绑定自适应（冗余但保持一致性）
      window.addEventListener("resize", () => {
        this.myChart.resize();
      });
    }
  }

}
</script>

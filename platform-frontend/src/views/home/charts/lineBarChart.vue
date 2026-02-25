/**
 * 柱折混合图组件（ECharts：支持双轴与多序列展示）
 */
<template>
    <!-- 图表容器：传入id以定位实例，宽度自适应 -->
    <div class="echart" :id="id" :style="{float:'left',width: '98%', height: '100%'}">
    </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: "LineBarChart",
  props: ["id", "title", "subTitle", "data"], // 组件入参：容器id/标题/副标题/数据结构
  data() {
    return {
      myChart: null,
      option: {
        tooltip: {
          trigger: 'axis', // 轴触发提示
          axisPointer: {
            type: 'cross', // 十字准星
            crossStyle: {
              color: '#999' // 准星颜色
            }
          }
        },
        toolbox: {
          feature: {
          }
        },
        legend: {
            left: "center", // 居中
            orient: 'horizontal', // 水平布局
            itemGap: 8 // 项间距
        },
        xAxis: [
          {
            type: 'category', // 类目轴
            axisPointer: {
                type: 'shadow' // 指示器为阴影
            },
            data: this.data.xAxis // X轴刻度
          }
        ],
        yAxis: [
          {
            type: 'value', // 左数值轴
            name: this.data.yLeft.name,  // 左轴名称
            min: 0, // 最小值
            max: this.data.yLeft.max, // 最大值
            interval: this.data.yLeft.max/5, // 刻度间隔
            axisLabel: {
              formatter: '{value}' // 标签格式
            },
            axisPointer: {
                status: 'hide' // 隐藏指示器
            },
          },
          {
            type: 'value', // 右数值轴
            name: this.data.yRight.name, // 右轴名称
            min: 0, // 最小值
            max: this.data.yRight.max, // 最大值
            interval: this.data.yRight.max/5, // 刻度间隔
            axisLabel: {
              formatter: '{value}' // 标签格式
            },
            axisPointer: {
                status: 'hide' // 隐藏指示器
            },
          }
        ],
        title: {
          text: this.title, // 主标题
          subtext: this.subTitle, // 副标题
          left: 'center' // 居中
        },
        grid: {
            left: '3%', // 左边距
            right: '3%', // 右边距
            bottom: '5%', // 底边距
            containLabel: true // 包含坐标轴标签
        },
		
        series: this.data.series // 系列：混合柱/线
      }
    }
  },
  // 挂载后：初始化图表实例
  mounted() {
    this.myChart = echarts.init(document.getElementById(this.id)); // 初始化图表实例
    this.initChart(); // 设置初次配置
  },
  methods:{
    // 初始化图表：应用配置并绑定自适应
    initChart() {
      this.myChart.setOption(this.option);
      // 随屏幕大小调节图表
      window.addEventListener("resize", () => {
        this.myChart.resize();
      });
    },
    // 更新图表：刷新坐标与系列配置
    updateChart(data) {
      if (data === null) { return; }
      this.option.xAxis[0].data = data.xAxis; // 更新X轴刻度
      this.option.series = data.series; // 更新序列数据
      this.option.yAxis[0].name = data.yLeft.name; // 左轴名称
      this.option.yAxis[0].max = data.yLeft.max; // 左轴最大值
      this.option.yAxis[0].interval = data.yLeft.max/5; // 左轴间隔
      this.option.yAxis[1].name = data.yRight.name; // 右轴名称
      this.option.yAxis[1].max = data.yRight.max; // 右轴最大值
      this.option.yAxis[1].interval = data.yRight.max/5; // 右轴间隔

      this.myChart.setOption(this.option); // 应用更新
      this.$forceUpdate(); // 强制组件刷新

      // 随屏幕大小调节图表
      window.addEventListener("resize", () => {
        this.myChart.resize();
      });
    }
  }

}
</script>

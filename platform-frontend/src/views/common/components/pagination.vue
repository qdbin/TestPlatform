/**
* 分页组件
*/ 
<template>
  <el-pagination class="page-box" @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="childMsg.currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="childMsg.pageSize" layout="total, sizes, prev, pager, next, jumper" :total="childMsg.total">
  </el-pagination>
</template>
<script>
export default {
  name: 'Pagination',
  props: ['childMsg'],
  data() {
    return {
      pageparm: {
        currentPage: this.childMsg.currentPage,
        pageSize: this.childMsg.pageSize
      }
    }
  },
  created() {},
  methods: {
    // 改变pageSize
    handleSizeChange(val) {
      this.pageparm.pageSize = val
      this.$emit('callFather', this.pageparm)
    },
    // 改变pageNum
    handleCurrentChange(val) {
      this.pageparm.currentPage = val
      this.$emit('callFather', this.pageparm)
    }
  }
}
</script>

<style>
.page-box {
  margin: 10px auto;
}
</style>

<template>
    <editor v-model="content" :lang="mode" @init="editorInit" :theme="theme" width="100%" :height="height"/>
</template>

<script>
    export default {
      name: "CodeEdit",
      components: { 
        editor: () => import('vue2-ace-editor')
      },
      props: {
        data:  {
          type:String
        },
        height: {
          type:Number
        },
        theme: {
          type: String,
          default() {
            return 'chrome'
          }
        },
        readOnly: {
          type: Boolean,
          default() {
            return false;
          }
        },
        mode: {
          type: String,
          default() {
            return 'text';
          }
        },
        modes: {
          type: Array,
          default() {
            return ['text', 'xml', 'html', 'python', 'sql'];
          }
        }
      },
      watch: {
        content(){
          this.$emit('update:data', this.content);
        },
        data(){
          this.content = this.data;
        }
      },
      data() {
        return {
          content: null
        }
      },
      mounted() {
        this.content = this.data;
      },
      methods: {
        editorInit: function (editor) {
          // 使用 Promise.all 并行加载所有需要的 brace 模块
          Promise.all([
            import('brace/ext/language_tools'),  // 代码提示工具
            ...this.modes.map(mode => import(`brace/mode/${mode}`)),  // 各种语言模式
            import(`brace/theme/${this.theme}`),  // 主题
            import('brace/snippets/javascript')  // JavaScript 代码片段
          ]).then(() => {
            // 所有模块加载完成后，设置编辑器为只读模式（如果需要）
            if (this.readOnly) {
              editor.setReadOnly(true);
            }
          }).catch(err => {
            console.error('Failed to load brace modules:', err);
          });
        },
      }
    }
</script>

<style scoped>

</style>

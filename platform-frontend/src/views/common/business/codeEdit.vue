<!--函数代码域组件-->
<template>
	<editor v-model="content" :lang="mode" @init="editorInit" :theme="theme" width="100%" :height="height"/>
</template>

<script>
// brace 的这些模块是“副作用引入”，不导出任何内容，仅在加载时向 Ace 注入功能
import 'brace/ext/language_tools'; // 语言工具扩展（副作用引入）
import 'brace/mode/text'; // 文本模式
import 'brace/mode/xml'; // XML 模式
import 'brace/mode/html'; // HTML 模式
import 'brace/mode/python'; // Python 模式
import 'brace/mode/sql'; // SQL 模式
import 'brace/theme/chrome'; // 主题（与默认值保持一致）
import 'brace/snippets/javascript'; // 代码片段（副作用引入）

export default {
	name: "CodeEdit",
	components: { editor: require('vue2-ace-editor')},
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
		// 在 Vite 环境中，require('brace/...') 会被转换成默认导入，而 brace 的这些文件是纯副作用脚本并不提供 default 导出，导致运行时报错
		editorInit: function (editor) {
			// 已将相关 brace 模块改为顶层静态 import（副作用），此处仅保留只读配置
			/*
				require('brace/ext/language_tools') //language extension prerequsite...
				this.modes.forEach(mode => {
					require('brace/mode/' + mode); //language
				});
				require('brace/theme/' + this.theme)
				require('brace/snippets/javascript') //snippet
			*/
			if (this.readOnly) {
				editor.setReadOnly(true);
			}
		},
	}
}
</script>

<style scoped>

</style>

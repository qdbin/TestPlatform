/**
 * element-ui消息提示封装（避免同屏重复提示同样内容）
 */
import { Message } from 'element-ui';


// 统一消息函数：同内容在同屏只展示一次
const resetMessage =(options) => {
  // 当前页面已存在的消息节点（由 Element UI 渲染出的 .el-message）
  let doms = document.getElementsByClassName('el-message');
  // 是否允许本次展示（默认允许）
  let canShow = true;
  // 若已存在同样文案（options.message），则本次不再弹出，避免重复提示
  for( let i=0; i<doms.length; i++){
    if(options.message == doms[i].getElementsByClassName('el-message__content')[0].innerHTML){
      canShow = false;
    }
  }
  // 没有任何消息或不存在相同文案时，正常弹出消息
  if(doms.length === 0 || canShow){
    Message(options);
  }
};

// 类型封装 message（动态挂载四个便捷方法）（message.success、message.warning、message.info、message.error）
['error','success','info','warning'].forEach(type => {
  resetMessage[type] = options => {
    // String示例：resetMessage.success('OK') → 变成 { message:'OK', type:'success' }
    if(typeof options === 'string') {
      options = {
        message:options
      }
    }
    options.type = type;
    return resetMessage(options);
  }
})

export const message = resetMessage; // 导出统一消息对象

/**
 * 使用示例（复制即可用）：
 * - 成功提示： message.success('保存成功')
 * - 警告提示： message.warning({ message: '参数有误', showClose: true })
 * - 信息防抖： 连续多次 message.info('正在加载…') 同屏只显示一条
 * - 错误可关闭： const h = message.error('服务器异常'); h.close();
 */

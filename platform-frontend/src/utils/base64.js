/**
 * Base64 转 Blob（用于二进制文件数据处理）
 */
export function b64toBlob(b64Data, contentType, sliceSize) {
  contentType = contentType || ''; // MIME类型
  sliceSize = sliceSize || 512; // 切片大小

  var byteCharacters = atob(b64Data);
  var byteArrays = [];

  for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    var slice = byteCharacters.slice(offset, offset + sliceSize);

    var byteNumbers = new Array(slice.length);
    for (var i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    var byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  return new Blob(byteArrays, {
    type: contentType // 指定MIME类型
  });
}
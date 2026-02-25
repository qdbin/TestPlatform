package com.autotest.common.utils;

import com.qiniu.util.*;
import okhttp3.*;

/**
 * 工具：七牛云图片上传（token:b64）
 * 用途：获取上传凭证并以Base64方式上传图片
 */
public class UploadUtils {

    /**
     * 获取上传凭证
     *
     * @param bucketName // 存储空间名称
     * @param ak         // 访问密钥AccessKey
     * @param sk         // 安全密钥SecretKey
     * @return String    // 上传凭证token
     *
     * 示例：getUpToken("images", ak, sk) -> "UpToken xxx"
     */
    public static String getUpToken(String bucketName,String ak, String sk) {
        Auth auth = Auth.create(ak, sk); // 创建鉴权对象
        return auth.uploadToken(bucketName, null, 3600, new StringMap().put("insertOnly", 1)); // 生成上传token
    }

    /**
     * 以Base64方式上传图片
     *
     * @param fileName    // 文件名（作为对象Key）
     * @param file64      // 图片Base64字符串（不含前缀）
     * @param uploadUrl   // 上传域名（七牛PUT64接口地址）
     * @param imageBucket // 存储空间名称
     * @param ak          // 访问密钥AccessKey
     * @param sk          // 安全密钥SecretKey
     *
     * 调用示例：
     *     uploadImageB64("a.png", base64, "https://up.qiniu.com", "images", ak, sk)
     */
    public static void uploadImageB64(String fileName, String file64, String uploadUrl,
                                      String imageBucket, String ak, String sk) throws Exception {
        String url = uploadUrl + "/putb64/-1/key/"+ UrlSafeBase64.encodeToString(fileName); // 拼接上传地址
        RequestBody body = RequestBody.create(null, file64); // 构造请求体
        // 构造请求（关键：设置内容类型与授权头）
        Request request = new Request.Builder().url(url).
                addHeader("Content-Type", "application/octet-stream").
                addHeader("Authorization", "UpToken " + getUpToken(imageBucket, ak, sk)).
                post(body).build();
        OkHttpClient client = new OkHttpClient(); // 创建HTTP客户端
        client.newCall(request).execute();        // 执行上传请求
    }

}

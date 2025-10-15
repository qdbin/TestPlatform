package com.autotest.common.utils;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.serializer.SerializerFeature;
import com.autotest.common.exception.FileUploadException;
import com.autotest.common.exception.LMException;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.FileCopyUtils;
import org.springframework.web.multipart.MultipartFile;

import javax.servlet.http.HttpServletResponse;
import java.io.*;

/**
 * 工具：文件读写/上传/下载（file:stream）
 * 用途：统一处理文件上传保存、JSON文件生成、删除、预览、下载
 */
public class FileUtils {

    /**
     * 上传通用文件
     *
     * @param uploadFile // 前端上传的文件对象
     * @param path       // 保存目录路径
     * @param name       // 保存文件名
     * @return String    // 保存后的完整文件路径
     *
     * 示例：uploadFile(file, "./data", "a.txt") -> "./data/a.txt"
     */
    public static String uploadFile(MultipartFile uploadFile, String path, String name) {
        if (uploadFile == null) {
            return null;
        }
        File testDir = new File(path);               // 创建保存目录
        if (!testDir.exists()) {
            testDir.mkdirs();                        // 不存在则创建
        }
        String filePath = testDir + "/" + name;     // 目标文件路径
        File file = new File(filePath);              // 目标文件
        try {
            uploadFile.transferTo(file);             // 保存上传文件
        } catch (IOException e) {
            throw new FileUploadException("文件上传失败");
        }
        return filePath;
    }

    /**
     * 生成JSON文件（格式化输出）
     *
     * @param json     // JSON对象内容
     * @param filePath // 输出文件路径
     */
    public static void createJsonFile(JSONObject json, String filePath){
        // PrettyFormat（格式化输出，即有缩进），WriteMapNullValue（保留值为null的字段，默认不保留），WriteDateUseDateFormat（将date日期格式转为格式化后的string字符串）
        String content = JSON.toJSONString(json, SerializerFeature.PrettyFormat, SerializerFeature.WriteMapNullValue, SerializerFeature.WriteDateUseDateFormat);
        try {
            File file = new File(filePath);                 // 目标文件

            // 如果父目录不存在，创建父目录
            if (!file.getParentFile().exists()) {
                file.getParentFile().mkdirs();
            }

            // 如果已存在,删除旧文件
            if (file.exists()) {
                file.delete();
            }
            file.createNewFile();                           // 创建新文件

            // 将格式化后的字符串写入文件
            Writer write = new OutputStreamWriter(new FileOutputStream(file), "UTF-8");
            write.write(content);                           // 写入内容
            write.flush();                                  // 刷新缓冲
            write.close();                                  // 关闭写入
        } catch (Exception e) {
            throw new LMException("json文件生成失败");
        }
    }

    /**
     * 删除文件并清理其所在目录
     *
     * @param path // 文件完整路径
     */
    public static void deleteFile(String path) {
        File file = new File(path);           // 文件对象
        if (file.exists()) {
            file.delete();                    // 删除文件
        }
        String dir = path.substring(0, path.lastIndexOf("/")); // 获取父目录
        File fileDir = new File(dir);
        if(fileDir.exists()){
            fileDir.delete();                 // 删除父目录
        }
    }

    /**
     * 递归删除目录
     *
     * @param path // 目录路径
     */
    public static void deleteDir(String path) {
        File file = new File(path);
        if (file.isDirectory()) {
            File[] files = file.listFiles();                // 列出子文件
            String dir = path.length() == 0 ? "" : path + "/";
            // 递归删除目录中的子目录下
            for (int i=0; i<files.length; i++) {
                deleteDir(dir + files[i].getName());       // 递归删除子项
            }
        }
        file.delete();                                      // 删除当前目录或文件
    }

    /**
     * 文件转字节数组
     *
     * @param tradeFile // 输入文件对象
     * @return byte[]    // 字节内容（失败返回null）
     */
    public static byte[] fileToByte(File tradeFile) {
        byte[] buffer = null;
        try (FileInputStream fis = new FileInputStream(tradeFile);
             ByteArrayOutputStream bos = new ByteArrayOutputStream();) {
            byte[] b = new byte[1024];
            int n;
            while ((n = fis.read(b)) != -1) {
                bos.write(b, 0, n);                         // 写入缓冲
            }
            buffer = bos.toByteArray();
        } catch (Exception ignored) {
        }
        return buffer;
    }

    /**
     * 上传测试文件并保持原文件名
     *
     * @param uploadFile // 上传文件对象
     * @param path       // 保存目录
     * @return String    // 保存后的路径
     */
    public static String uploadTestFile(MultipartFile uploadFile, String path) {
        return uploadFile(uploadFile, path, uploadFile.getOriginalFilename());
    }

    /**
     * 下载文件输出至响应
     *
     * @param path     // 文件路径
     * @param response // Http响应对象
     */
    public static void downloadFile(String path, HttpServletResponse response) {
        File file = new File(path);
        if (!file.isFile()) {
            throw new LMException("文件不存在");
        }
        // 设置下载响应头（关键：attachment 指示下载）
        response.setHeader(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + file.getName() + "\"");
        try {
            // 构造文件输入流
            FileInputStream fileInputStream = new FileInputStream(file);
            BufferedInputStream bufferedInputStream = new BufferedInputStream(fileInputStream); // 提升读取效率
            BufferedOutputStream bufferedOutputStream = new BufferedOutputStream(response.getOutputStream()); // 响应输出流
            FileCopyUtils.copy(bufferedInputStream, bufferedOutputStream);                  // 拷贝输出
        } catch(Exception e){
            throw new LMException("文件下载失败");
        }
    }

    /**
     * 预览图片（返回二进制）
     *
     * @param path // 图片文件路径
     * @return ResponseEntity<byte[]> // 图片字节响应（PNG）
     */
    public static ResponseEntity<byte[]> previewImage(String path) {
        File file = new File(path);
        byte[] fileByte= FileUtils.fileToByte(file); // 读取字节
        if(fileByte == null){
            return null;                            // 读取失败返回空
        }
        return ResponseEntity.ok()
                .contentType(MediaType.IMAGE_PNG)  // 指定PNG类型
                .body(fileByte);                   // 返回字节内容
    }

}

package com.autotest.common.utils;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.zip.CRC32;
import java.util.zip.CheckedOutputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * 工具：目录/文件压缩为zip（src:zip）
 * 用途：递归打包目录或文件，生成目标zip归档
 */
public class ZipUtils {

    /**
     * 将源目录压缩到目标路径下
     *
     * @param resourcesPath // 源目录/文件路径
     * @param targetPath    // 目标目录路径
     * @param targetName    // 压缩包名称（不含扩展名）
     *
     * 示例：compress("./src", "./out", "archive") -> 生成 out/archive.zip
     */
    public static void compress(String resourcesPath, String targetPath, String targetName) throws Exception {
        // task目录
        File resourcesFile = new File(resourcesPath);

        // 目标输出目录，目录不存在，创建父目录
        File targetFile = new File(targetPath);
        if (!targetFile.exists()) {
            targetFile.mkdirs();
        }

        // 创建包装输出流
        FileOutputStream outputStream = new FileOutputStream(targetPath+"/"+targetName+".zip"); // 文件输出流
        CheckedOutputStream cos = new CheckedOutputStream(outputStream, new CRC32());                   // 校验流（CRC32）
        ZipOutputStream out = new ZipOutputStream(cos);                                                 // zip输出流

        // 递归写入条目
        createCompressedFile(out, resourcesFile, "/"+targetName);

        out.close(); // 关闭zip流
    }

    /**
     * 递归创建压缩条目
     *
     * @param out  // 压缩输出流
     * @param file // 当前文件或目录
     * @param dir  // zip内路径前缀
     */
    public static void createCompressedFile(ZipOutputStream out, File file, String dir) throws Exception {
        // 目录file
        if (file.isDirectory()) {
            // 得到file_list
            File[] files = file.listFiles();

            // 将文件夹添加到指定目
            out.putNextEntry(new ZipEntry(dir + "/"));
            dir = dir.length() == 0 ? "" : dir + "/";

            // 循环将文件夹中的文件打包
            for (int i = 0; i < files.length; i++) {
                // 递归处理子项
                createCompressedFile(out, files[i], dir + files[i].getName());
            }
        }
        // 非目录file
        else {
            // 当前是文件，打包为条目
            // 文件输入流（读文件）
            BufferedInputStream bis = new BufferedInputStream(new FileInputStream(file));
            ZipEntry entry = new ZipEntry(dir);
            out.putNextEntry(entry); // 写入条目
            int j = 0;
            byte[] buffer = new byte[1024];

            while ((j = bis.read(buffer)) > 0) {
                out.write(buffer, 0, j); // 写入字节块
            }
            // 关闭输入流
            bis.close();
        }
    }
}

package com.autotest.common.utils;

import javax.imageio.ImageIO;
import javax.xml.bind.DatatypeConverter;
import java.awt.image.BufferedImage;
import java.io.*;

/**
 * 工具：图片Base64转文件（base64:image）
 * 用途：将Base64字符串解析并输出为PNG图片文件
 */
public class ImageUtils {

    /**
     * Base64转图片并保存
     *
     * @param base64Code // 图片Base64（不含data:image/png;base64,前缀）
     * @param path       // 输出文件路径（包含文件名）
     *
     * 示例：convertBase64ToImage(base64, "./output/a.png")
     */
    public static void convertBase64ToImage(String base64Code, String path) throws IOException {
        BufferedImage image = null;             // 图片对象
        byte[] imageByte = null;                // 原始字节
        imageByte = DatatypeConverter.parseBase64Binary(base64Code); // 解析Base64
        ByteArrayInputStream bis = new ByteArrayInputStream(imageByte); // 构造输入流
        image = ImageIO.read(new ByteArrayInputStream(imageByte));      // 读取为BufferedImage
        bis.close();                                                     // 关闭流
        File outputfile = new File(path);                                // 目标文件
        if (!outputfile.getParentFile().exists()) { // 如果父目录不存在，创建父目录
            outputfile.getParentFile().mkdirs();
        }
        ImageIO.write(image, "png", outputfile);                       // 写出PNG文件
    }
}

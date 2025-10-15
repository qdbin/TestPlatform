package com.autotest.service;

import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import javax.annotation.Resource;
import javax.mail.MessagingException;
import javax.mail.internet.MimeMessage;

/**
 * 类型: Service
 * 职责: 发送报告邮件/通知邮件；封装邮件发送的基础能力
 * 高频功能: (1) 构建邮件内容 (2) 设置收发人与主题 (3) 发送HTML邮件
 *
 * 使用示例:
 *  SendMailService.sendReportMail(from, to, title, htmlContent)
 */
@Service
public class SendMailService {

    @Resource
    private JavaMailSender javaMailSender;

    /**
     * 发送报告邮件（支持HTML内容）
     *
     * @param from    // 发件人邮箱
     * @param to      // 收件人邮箱
     * @param title   // 邮件主题
     * @param content // 邮件正文（支持HTML）
     * @throws MessagingException // 构建或发送邮件失败时抛出
     *
     * 使用示例:
     *  // 入参示例
     *  // from="noreply@example.com", to="user@example.com", title="报告通知", content="<h1>成功</h1>"
     *  // 调用示例
     *  // sendReportMail(from, to, title, content)
     *  // 返回值示例: 无返回，异常时抛 MessagingException
     */
    public void sendReportMail(String from, String to, String title, String content) throws MessagingException {
        // 创建邮件消息对象
        MimeMessage message = javaMailSender.createMimeMessage();

        // 构建Multipart消息体（true表示使用multipart）
        MimeMessageHelper helper = new MimeMessageHelper(message, true);
        helper.setFrom(from);
        helper.setTo(to);
        helper.setSubject(title);
        helper.setText(content, true); // 第二个参数true表示HTML内容

        // 发送邮件
        javaMailSender.send(message);
    }

}

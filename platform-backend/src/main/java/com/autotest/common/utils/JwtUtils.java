package com.autotest.common.utils;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTVerifier;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.exceptions.TokenExpiredException;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.autotest.domain.Engine;
import com.autotest.domain.User;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * 工具：JWT令牌生成与校验
 *     用途：生成平台/引擎token，校验并解析token
 */
public class JwtUtils {
    // 验签工具
    private static final String SECRET = "Test_Secret"; // 加密秘钥

    private static final long WEB_EXPIRATION = 7200L;   //平台token过期时间 2小时

    private static final long ENGINE_EXPIRATION = 604800L;  //引擎token过期时间 7天

    /**
     * 生成平台token
     *
     * @param user   用户实体（包含 `id`、`username`、`account`、`password`）
     * @return String 平台 JWT 字符串
     *
     * 示例：claims 包含 {id, username, account, password}
     */
    public static String createWebToken(User user) {
        Date expireDate = new Date(System.currentTimeMillis() + WEB_EXPIRATION*1000); // 计算过期时间
        Map<String, Object> map = new HashMap<>();           // 组装头部参数
        map.put("alg", "HS256");
        map.put("typ", "JWT");
        return JWT.create()
                .withHeader(map)                             // 设置头部
                .withClaim("id", user.getId())              // 载荷：用户ID
                .withClaim("username", user.getUsername())  // 载荷：用户名
                .withClaim("account", user.getAccount())    // 载荷：账号
                .withClaim("password", user.getPassword())  // 载荷：密码（建议生产不放敏感信息）
                .withExpiresAt(expireDate)                   // 设置过期时间
                .withIssuedAt(new Date())                    // 设置签发时间
                .sign(Algorithm.HMAC256(SECRET));            // 使用密钥签名
    }

    /**
     * 生成引擎token
     *
     * @param engine 引擎实体（包含 `id` 与 `secret`）
     * @return String 引擎 JWT 字符串
     */
    public static String createEngineToken(Engine engine) {
        Date expireDate = new Date(System.currentTimeMillis() + ENGINE_EXPIRATION*1000); // 计算过期时间
        Map<String, Object> map = new HashMap<>();           // 组装头部参数
        map.put("alg", "HS256");
        map.put("typ", "JWT");
        String token = JWT.create()
                .withHeader(map)                             // 设置头部
                .withClaim("engineId", engine.getId())      // 载荷：引擎ID
                .withClaim("engineSecret", engine.getSecret()) // 载荷：引擎密钥
                .withExpiresAt(expireDate)                   // 设置过期时间
                .withIssuedAt(new Date())                    // 设置签发时间
                .sign(Algorithm.HMAC256(SECRET));            // 使用密钥签名
        return token;
    }

    /**
     * 校验并解析 JWT 字符串
     * @param token 待校验的 JWT 字符串
     * @return DecodedJWT 解析后的 JWT 对象（包含头部/载荷/签名信息）
     * @throws TokenExpiredException   当 token 过期时抛出
     * @throws JWTVerificationException 当验签失败或格式错误时抛出
     */
    public static DecodedJWT verifyToken(String token) {
        DecodedJWT jwt = null; // 初始化解析结果
        try {
            JWTVerifier verifier = JWT.require(Algorithm.HMAC256(SECRET)).build(); // 构造验证器
            jwt = verifier.verify(token);
        } catch (TokenExpiredException e) {
            // 时间校验出错抛出过期
            throw new TokenExpiredException("token已过期");
        } catch (Exception e) {
            // 解码异常抛出校验出错
            throw new JWTVerificationException("token校验出错");
        }
        return jwt; // 返回解析后的令牌对象
    }
}

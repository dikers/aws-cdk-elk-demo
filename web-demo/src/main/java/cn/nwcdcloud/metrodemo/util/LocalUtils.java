package cn.nwcdcloud.metrodemo.util;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.UnknownHostException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LocalUtils {
    private static Logger logger = LoggerFactory.getLogger(LocalUtils.class);

    public static String getIP() {
        try {
            InetAddress ia = InetAddress.getLocalHost();
            return ia.getHostAddress();
        } catch (UnknownHostException e) {
            logger.warn("获取本地IP出错", e);
            return null;
        }
    }

    public static String getMAC() {
        try {
            InetAddress ia = InetAddress.getLocalHost();
            byte[] mac = NetworkInterface.getByInetAddress(ia).getHardwareAddress();
            StringBuffer sb = new StringBuffer("");
            for (int i = 0; i < mac.length; i++) {
                if (i != 0) {
                    sb.append("-");
                }
                // 字节转换为整数
                int temp = mac[i] & 0xff;
                String str = Integer.toHexString(temp);
                if (str.length() == 1) {
                    sb.append("0" + str);
                } else {
                    sb.append(str);
                }
            }
            return sb.toString().toUpperCase();
        } catch (Exception e) {
            logger.warn("获取本地MAC出错", e);
            return null;
        }
    }

    public static void main(String[] args) {
        logger.debug(getIP());
        logger.debug(getMAC());
    }
}

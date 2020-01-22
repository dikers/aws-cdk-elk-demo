package cn.nwcdcloud.metrodemo.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {
	private final Logger logger = LoggerFactory.getLogger(getClass());
	private int linkMax = 89999, linkMin = 10000;
	private int errMax = 10, errMin = 1;
	private int timeMax = 5, timeMin = 1;

	@ResponseBody
	@RequestMapping("/")
	public String index(Integer total, Integer tps) {
		if (tps == null) {
			tps = 1;
		}
		if (tps > 100) {
			tps = 100;
		}
		if (total == null) {
			total = 1;
		}
		if (total > 100) {
			total = 100;
		}
		int sleep = 1000 / tps;
		for (int i = 1; i <= total; i++) {
			logger.info(disposeLog());
			if (i < total) {
				try {
					Thread.sleep(sleep);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
		}
		return "OK";
	}

	private String disposeLog() {
		int linkId = (int) (Math.random() * (linkMax - linkMin) + linkMin);
//		int devId = linkId + 10000;
		String ip = "172.19.71.224";
		int errCode = 9999;
		String errMsg = "执行成功";
		int errId = (int) (Math.random() * (errMax - errMin) + errMin);
		if (errId >= 8) {
			errCode = 1111;
			errMsg = "执行错误";
		}
		int time = (int) (Math.random() * (timeMax - timeMin) + timeMin);
		return String.format("-%s~设备标识~%s~%s~%s~%s~%s", linkId, ip, errCode, errMsg, "T", time);
	}
}

package cn.nwcdcloud.metrodemo.controller;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import javax.servlet.http.HttpServletRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.ModelAndView;

import com.alibaba.fastjson.JSONObject;

@RestController
@CrossOrigin
public class TestController {
	private final Logger logger = LoggerFactory.getLogger(getClass());
	private int linkMax = 89999, linkMin = 10000;
	private int errMax = 10, errMin = 1;
	private int timeMax = 5, timeMin = 1;

	@RequestMapping("/")
	public ModelAndView index(HttpServletRequest request) {

		String localHostIp = "127.0.0.1";
		try {
			InetAddress address = InetAddress.getLocalHost();
			localHostIp = address.getHostAddress();
		} catch (UnknownHostException e) {
			localHostIp = "unknown";
			e.printStackTrace();
		}
		ModelMap model = new ModelMap();
		model.addAttribute("localHostIp", localHostIp);
		return new ModelAndView("index", model);
	}

	@ResponseBody
	@RequestMapping("/send")
	public String send(Integer total, Integer tps) {

//		if (tps == null) {
//			tps = 1;
//		}
//		if (tps > 100) {
//			tps = 100;
//		}
		if (total == null) {
			total = 1;
		}
		if (total > 100) {
			total = 100;
		}
//		int sleep = 1000 / tps;
		for (int i = 0; i < total; i++) {
			logger.info(disposeLog());
//			if (i < total) {
//				try {
//					Thread.sleep(sleep);
//				} catch (InterruptedException e) {
//					e.printStackTrace();
//				}
//			}
		}
		LocalDateTime now = LocalDateTime.now();
		DateTimeFormatter formatter2 = DateTimeFormatter.ofPattern("yyyy-MM-dd hh:mm:ss");

		JSONObject result = new JSONObject();
		result.put("count", total);
		result.put("time", now.format(formatter2));
		return JSONObject.toJSONString(result);
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

	@ResponseBody
	@RequestMapping("/crontask")
	public String crontask() {
		return "OK";
	}

	@ResponseBody
	@RequestMapping("/version")
	public String version() {
		return "V2,";
	}

	@ResponseBody
	@RequestMapping("/getenv")
	public String getenv(String name) {
		return System.getenv(name);
	}

	@ResponseBody
	@RequestMapping("/getProperty")
	public String getProperty(String name) {
		return System.getProperty(name);
	}
}

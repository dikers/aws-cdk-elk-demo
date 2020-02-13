package cn.nwcdcloud.metrodemo.util;

public class MathUtils {

	public static long getSum(long max) {
		if (max < 1) {
			return 0;
		}
		long sum = 0;
		for (long i = 1; i <= max; i++) {
			sum += i;
		}
		return sum;
	}

	public static void main(String[] args) {
		long begin = System.currentTimeMillis();
		System.out.println(getSum(2000000000L));
		long end = System.currentTimeMillis();
		System.out.println(end - begin);
	}
}

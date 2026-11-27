// سيناريو k6 قصير — نسخ محلية فقط (127.0.0.1)، لا إنتاج بلا إذن المالك
import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = {
  vus: 5, duration: '10s',
  thresholds: { http_req_failed: ['rate<0.01'], http_req_duration: ['p(95)<500'] },
};
const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8080';
export default function () {
  const r = http.get(`${BASE}/`);
  check(r, { 'الحالة 200': (x) => x.status === 200 });
  sleep(0.2);
}

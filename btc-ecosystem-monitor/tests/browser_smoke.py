"""Optional local browser smoke test: python tests/browser_smoke.py."""
import functools
import json
from pathlib import Path
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT/'web')))
threading.Thread(target=server.serve_forever, daemon=True).start()
errors=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='networkidle')
        page.get_by_role('heading',name='BTC 生态，一站观察').wait_for()
        assert page.get_by_text('等待首次采集',exact=True).count()==1
        (ROOT/'.local').mkdir(exist_ok=True)
        page.screenshot(path=str(ROOT/'.local/desktop.png'),full_page=True)
        page.locator('[data-nav="projects"]').click()
        page.locator('#project-search').fill('Bitlight')
        assert page.locator('#project-results tbody tr').count()==1
        page.locator('[data-favorite="bitlight"]').click()
        page.locator('[data-project="bitlight"]').click()
        page.get_by_role('dialog').wait_for()
        assert '0x477C2c' in page.locator('#detail-content').inner_text()
        page.get_by_role('button',name='关闭',exact=True).click()
        page.locator('[data-nav="news"]').click()
        page.locator('#news-window').select_option('1')
        assert '此窗口没有可列示记录' in page.locator('#news-results').inner_text()
        for route in ('feedback','markets','reports','settings'):
            page.locator(f'[data-nav="{route}"]').click()
            page.wait_for_timeout(50)
        page.locator('#config-editor').fill('{"invalid":true}')
        page.locator('[data-action="save-config"]').click()
        assert '配置格式不正确' in page.locator('#toast').inner_text()
        page.locator('[data-action="reset-config"]').click()
        page.locator('[name="title"]').fill('<img src=x onerror=alert(1)>')
        page.locator('[name="url"]').fill('https://example.com/source')
        page.locator('[name="summary"]').fill('Browser smoke fixture only; not committed as evidence.')
        page.locator('#evidence-form button[type="submit"]').click()
        assert '1 条公告草稿' in page.locator('#evidence-form').inner_text()
        page.locator('[data-nav="reports"]').click()
        with page.expect_download() as download:
            page.locator('[data-action="download-report"]').click()
        assert download.value.suggested_filename.endswith('.md')
        page.set_viewport_size({'width':390,'height':844})
        page.locator('[data-nav="overview"]').click()
        page.screenshot(path=str(ROOT/'.local/mobile.png'),full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile horizontal overflow'
        assert not errors, errors
        browser.close()
        print(json.dumps({'routes':7,'browserErrors':errors,'mobileOverflow':False,'search':'passed','favorites':'passed','detail':'passed','configValidation':'passed','evidenceDraft':'passed','download':'passed'}))
finally:
    server.shutdown()
    server.server_close()

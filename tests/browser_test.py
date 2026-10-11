# Real Chromium tests (Playwright). Run: python3 tests/browser_test.py   (needs: pip install playwright && playwright install chromium)
import subprocess,time,os,json,io,urllib.request,urllib.error,sys
from playwright.sync_api import sync_playwright
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(D);SC=os.path.join(D,'screenshots');os.makedirs(SC,exist_ok=True)
P=8099;B=f'http://127.0.0.1:{P}';SID='testsess';KEY='testkey'
R=[]
def ok(n,c,x=''):R.append(('PASS ' if c else 'FAIL ')+n+('' if c else ' -> '+str(x)))
srv=subprocess.Popen(['node','server.js'],cwd=ROOT,env={**os.environ,'PORT':str(P),'SESSION_ID':SID,'SESSION_KEY':KEY},stdout=subprocess.DEVNULL);time.sleep(1)
def put(key,s=SID):
    rq=urllib.request.Request(f'{B}/api/state?s={s}',data=json.dumps({'from':'x','state':{}}).encode(),method='PUT',headers={'x-key':key,'content-type':'application/json'})
    try:return urllib.request.urlopen(rq).status
    except urllib.error.HTTPError as e:return e.code
try:
  with sync_playwright() as p:
    br=p.chromium.launch()
    ctx=lambda w,h,**k:br.new_context(viewport={'width':w,'height':h},**k)
    # --- server sync across independent browser contexts (separate storage) ---
    A=ctx(1650,940).new_page();O=ctx(1920,1080).new_page();M=ctx(390,844,is_mobile=True,has_touch=True).new_page()
    A.goto(f'{B}/?s={SID}&k={KEY}');O.goto(f'{B}/?s={SID}#/overlay');M.goto(f'{B}/?s={SID}&k={KEY}');time.sleep(1)
    ev=lambda pg,s:pg.evaluate(s)
    A.click('#start');time.sleep(1.6);ok('server sync: start reaches overlay (separate context)',ev(O,'S.T.run')==True and abs(ev(O,'el()')-ev(A,'el()'))<.6,(ev(O,'el()'),ev(A,'el()')))
    A.click('#pause');time.sleep(.6);ok('server sync: pause',ev(O,'S.T.run')==False and abs(ev(O,'el()')-ev(A,'el()'))<.05)
    A.click('#pause');time.sleep(.6);ok('server sync: resume',ev(O,'S.T.run')==True)
    A.fill('[data-k="ev.title"]','SERVER SYNC');time.sleep(.6);ok('server sync: event text',ev(O,'S.ev.title')=='SERVER SYNC')
    A.click('[data-th=gold]');time.sleep(.4);ok('server sync: theme',ev(O,'S.st.theme')=='gold')
    A.uncheck('[data-k="st.show.coach"]');time.sleep(.4);ok('server sync: visibility',ev(O,"ovHTML().includes('COACH')")==False)
    A.click('#reset');time.sleep(.5);ok('server sync: reset',ev(O,'S.T.run')==False and ev(O,'el()')==0)
    M.click('#start');time.sleep(1.2);ok('phone (3rd context) controls session; dashboard and overlay follow',ev(A,'S.T.run')==True and ev(O,'S.T.run')==True and ev(M,'S.T.run')==True)
    M.click('#reset');time.sleep(.4)
    O.reload();time.sleep(1);ok('overlay refresh recovers state from server',ev(O,'S.ev.title')=='SERVER SYNC' and ev(O,'S.st.theme')=='gold')
    ok('write without key rejected (403)',put('')==403);ok('write with wrong key rejected (403)',put('nope')==403);ok('write with wrong session rejected (403)',put(KEY,'bad')==403)
    O2=ctx(800,600).new_page();O2.goto(f'{B}/?s={SID}#/overlay');time.sleep(.5);O2.evaluate('S.ev.title="HACK";save()');time.sleep(.6)
    ok('overlay URL (no key) cannot control session',ev(A,'S.ev.title')=='SERVER SYNC')
    # --- overlay transparency + geometry ---
    for w,h in [(1920,1080),(1280,720),(1600,900)]:
        O.set_viewport_size({'width':w,'height':h});time.sleep(.4)
        bg=O.evaluate("[getComputedStyle(document.documentElement).backgroundColor,getComputedStyle(document.body).backgroundColor]")
        ok(f'overlay {w}x{h}: html/body background transparent',all(x in('rgba(0, 0, 0, 0)','transparent') for x in bg),bg)
        im=Image.open(io.BytesIO(O.screenshot(omit_background=True))).convert('RGBA')
        ok(f'overlay {w}x{h}: alpha=0 on empty area',im.getpixel((w//2,h-20))[3]==0 and im.getpixel((5,h-5))[3]==0)
        ok(f'overlay {w}x{h}: no scrollbars',O.evaluate('document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight'))
        r=O.evaluate("['#L','.C','#R','#LV','#W'].map(s=>{const e=document.querySelector(s).getBoundingClientRect();return[e.left,e.top,e.right,e.bottom]})")
        ok(f'overlay {w}x{h}: all zones inside viewport',all(a[0]>=-1 and a[1]>=-1 and a[2]<=w+1 and a[3]<=h+1 for a in r),r)
        if w==1920:O.screenshot(path=os.path.join(SC,'overlay_1920x1080.png'),omit_background=True)
    ok('overlay: no dashboard, nav or checkerboard',O.evaluate("!document.querySelector('nav,.chk,.grid')"))
    # --- responsive dashboard ---
    for w,h,cols in [(1920,1080,5),(1650,940,5),(1440,900,5),(1280,800,3),(1024,768,3),(768,1024,1),(390,844,1)]:
        pg=ctx(w,h).new_page();pg.goto(B+'/');time.sleep(.6)
        gc=pg.evaluate("getComputedStyle(document.querySelector('.grid')).gridTemplateColumns.split(' ').length")
        ok(f'dashboard {w}px: {cols} columns',gc==cols,gc)
        ok(f'dashboard {w}px: no page-level horizontal overflow',pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),pg.evaluate('[document.documentElement.scrollWidth,innerWidth]'))
        ok(f'dashboard {w}px: preview not clipped',pg.evaluate("(()=>{const p=document.querySelector('.grid .chk').getBoundingClientRect(),s=document.querySelector('.grid .strip-in').getBoundingClientRect();return s.right<=p.right+1&&s.bottom<=p.bottom+1})()"))
        if w>=1440:
            ok(f'dashboard {w}px: timer digits inside dial',pg.evaluate("(()=>{const c=document.querySelector('#hero .C').getBoundingClientRect();return [...document.querySelectorAll('#hero .C .D')].every(e=>{const r=document.createRange();r.selectNodeContents(e);const b=r.getBoundingClientRect();return b.left>c.left+12&&b.right<c.right-12&&Math.abs((b.left+b.right)/2-(c.left+c.right)/2)<8})})()"))
        pg.screenshot(path=os.path.join(SC,f'dashboard_{w}.png'),full_page=(w<1000));pg.context.close()
    # --- same-profile BroadcastChannel sync (no server) ---
    c=ctx(1650,940);a=c.new_page();o=c.new_page();a.goto(B+'/');o.goto(B+'/#/overlay');time.sleep(.6)
    a.click('#start');time.sleep(.8);ok('same-profile BroadcastChannel sync',ev(o,'S.T.run')==True)
    # --- timer accuracy (real browser, background tab) ---
    a.click('#reset');a.fill('[data-k="tm.m"]','10');a.click('#start');o.bring_to_front();time.sleep(8);a.bring_to_front();e,real=ev(a,'[el(),(Date.now()+OFF-S.T.t0)/1000]')
    ok('timer accuracy 8 s incl. 8 s in background tab (|err|<0.15 s)',abs(e-real)<.15,(e,real))
    a.click('#reset')
    # --- logo upload in real browser ---
    buf=io.BytesIO();Image.new('RGBA',(40,40),(255,0,0,255)).save(buf,'PNG')
    a.set_input_files('#file',files=[{'name':'l.png','mimeType':'image/png','buffer':buf.getvalue()}]);time.sleep(.4);ok('PNG upload',ev(a,'S.logo').startswith('data:image/png'))
    a.reload();time.sleep(.6);ok('logo persists after reload',ev(a,'S.logo').startswith('data:image/png'));a.click('#rm');ok('logo remove',ev(a,'S.logo')=='')
    a.set_input_files('#file',files=[{'name':'e.svg','mimeType':'image/svg+xml','buffer':b'<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><script>1</script></svg>'}]);time.sleep(.4);ok('malicious SVG rejected',ev(a,'S.logo')=='')
    a.set_input_files('#file',files=[{'name':'g.svg','mimeType':'image/svg+xml','buffer':b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="red"/></svg>'}]);time.sleep(.4);ok('safe SVG accepted and renders',ev(a,'S.logo').startswith('data:image/svg')and a.evaluate("[...document.querySelectorAll('#hero img')].some(i=>i.complete&&i.naturalWidth>0)"));a.click('#rm')
    # --- copy URL ---
    c.grant_permissions(['clipboard-read','clipboard-write']);a.goto(f'{B}/?s={SID}&k={KEY}');time.sleep(.5);a.click('#copy');time.sleep(.3);cb=a.evaluate('navigator.clipboard.readText()')
    ok('Copy URL puts overlay URL on clipboard without control key',cb.endswith('#/overlay') and 'k=' not in cb and 's='+SID in cb,cb)
    with a.context.expect_page() as np:a.click('#test')
    ok('Test in new tab opens overlay',np.value.url.endswith('#/overlay'))
    # --- local file:// mode (no server) ---
    FU='file://'+os.path.join(ROOT,'index.html')
    fc=ctx(1650,940);fa=fc.new_page();fo=fc.new_page();fa.goto(FU);fo.goto(FU+'#/overlay');time.sleep(.8)
    fa.click('#start');time.sleep(.8);ok('file://: start reaches overlay (same profile)',ev(fo,'S.T.run')==True)
    fa.fill('[data-k="ev.title"]','FILE MODE');fa.fill('[data-k="ev.sub"]','SUB');fa.fill('[data-k="ev.tag"]','TAG');fa.fill('[data-k="ev.loc"]','LOC');fa.fill('[data-k="ev.date"]','DATE');fa.fill('[data-k="wod.title"]','WT');fa.fill('[data-k="wod.coach"]','COACHX');fa.fill('[data-k="wod.notes"]','N1|N2');time.sleep(.6)
    ok('file://: all event/WOD text fields sync',ev(fo,"S.ev.title=='FILE MODE'&&['FILE','MODE','SUB','TAG','LOC','DATE','WT','COACHX','N1','N2'].every(x=>ovHTML().includes(x))"))
    fa.click('#add');fa.click('[data-mv="1"][data-d="-1"]');time.sleep(.5);ok('file://: exercise list sync',ev(fo,'S.wod.rows.length')==4)
    fa.click('[data-m=intervals]');fa.fill('[data-k="tm.wm"]','2');fa.fill('[data-k="tm.rs"]','45');fa.fill('[data-k="tm.rounds"]','7');time.sleep(.6)
    ok('file://: timer mode, work/rest and round settings sync',ev(fo,'[S.tm.mode,S.tm.wm,S.tm.rs,S.tm.rounds].join()')=='intervals,2,45,7')
    fa.set_input_files('#file',files=[{'name':'l.png','mimeType':'image/png','buffer':buf.getvalue()}]);time.sleep(.6);ok('file://: logo upload syncs',ev(fo,'S.logo').startswith('data:image/png'))
    fa.click('#rm');time.sleep(.5);ok('file://: logo remove syncs',ev(fo,'S.logo')=='')
    fa.uncheck('[data-k="st.show.timer"]');time.sleep(.5);ok('file://: show/hide syncs',ev(fo,"!ovHTML().includes('class=\"C\"')"))
    fo.reload();time.sleep(.8);ok('file://: overlay refresh keeps current data',ev(fo,'S.ev.title')=='FILE MODE')
    # poll-only fallback: no BroadcastChannel and no storage events delivered
    pc=ctx(1650,940);pa_=pc.new_page();po=pc.new_page()
    po.add_init_script("delete window.BroadcastChannel;const _a=window.addEventListener;window.addEventListener=function(t,...r){if(t==='storage')return;return _a.call(this,t,...r)}")
    pa_.goto(FU);po.goto(FU+'#/overlay');time.sleep(.8);pa_.fill('[data-k="ev.title"]','POLL ONLY');time.sleep(1.0)
    ok('fallback: storage polling syncs when BroadcastChannel and storage events are unavailable',ev(po,'S.ev.title')=='POLL ONLY')
    pa_.click('#start');time.sleep(1.0);ok('fallback: running timer syncs by polling',ev(po,'S.T.run')==True)
    # different profile (like OBS vs Chrome): documented limitation
    xo=ctx(1920,1080).new_page();xo.goto(FU+'#/overlay');time.sleep(.5);fa.fill('[data-k="ev.title"]','CROSS PROFILE');time.sleep(1.0)
    ok('KNOWN LIMITATION confirmed: a different browser profile does NOT receive local-mode updates (server mode required)',ev(xo,'S.ev.title')!='CROSS PROFILE')
    # --- debug mode, fixed storage key, 500 ms poll ---
    dc=ctx(1650,940);da=dc.new_page();dov=dc.new_page();logs=[]
    da.on('console',lambda m:logs.append(m.text));dov.on('console',lambda m:logs.append(m.text))
    da.goto(FU+'?debug=1');dov.goto(FU+'?debug=1#/overlay');dov.wait_for_timeout(800)
    da.fill('[data-k="ev.title"]','TEST 123');dov.wait_for_timeout(1300)
    ok('debug: dashboard logs "Dashboard saved state"',any('Dashboard saved state' in l for l in logs),logs[:3])
    ok('debug: overlay logs "Overlay received state"',any('Overlay received state' in l for l in logs),logs[:3])
    ok('debug: state stored under fixed key CROSSFIT_OVERLAY_STATE',json.loads(da.evaluate('localStorage.getItem("CROSSFIT_OVERLAY_STATE")'))['ev']['title']=='TEST 123')
    ok('title CROSSFIT OPEN -> TEST 123 reaches same-profile overlay without refresh',ev(dov,'S.ev.title')=='TEST 123')
    ok('debug status line shows only in debug mode',dov.evaluate("document.body.innerText.includes('CFO debug')") and not fo.evaluate("document.body.innerText.includes('CFO debug')"))
    # --- OBS WebSocket bridge against a protocol test double (real OBS delivery into browser sources is simulated) ---
    ml='/tmp/obs_ws_log.txt';open(ml,'w').close()
    mock=subprocess.Popen(['node','tests/mock_obs.js','4466',ml],cwd=ROOT,env={**os.environ,'NODE_PATH':os.environ.get('NODE_PATH','')});time.sleep(.8)
    wd=ctx(1650,940).new_page();wo=ctx(1920,1080).new_page();wlogs=[]
    wd.on('console',lambda m:wlogs.append(m.text));wo.on('console',lambda m:wlogs.append(m.text))
    wd.goto(FU+'?debug=1');wo.goto(FU+'?debug=1#/overlay');wd.click('[data-t="5"]')
    wd.fill('#wsa','ws://127.0.0.1:4466');wd.fill('#wsp','wrong');wd.click('#wsb');wd.wait_for_timeout(800)
    ok('obs-ws: wrong password rejected with message',wd.inner_text('#wss').startswith('Wrong OBS'),wd.inner_text('#wss'))
    wd.fill('#wsp','secret');wd.click('#wsb');wd.wait_for_timeout(900)
    ents=[json.loads(l) for l in open(ml) if l.strip()]
    ok('obs-ws: authentication handshake accepted',any(e['type']=='identify' and e['ok'] for e in ents) and 'Connected' in wd.inner_text('#wss'),wd.inner_text('#wss'))
    def last():
        rq=[json.loads(l) for l in open(ml) if l.strip()];rq=[e['d'] for e in rq if e['type']=='request'];return rq[-1]['requestData']
    def deliver(rd):wo.evaluate("d=>window.dispatchEvent(new CustomEvent('cfo-state',{detail:d}))",rd['requestData']['event_data'])
    wd.click('[data-t="0"]');wd.fill('[data-k="ev.title"]','ABC TEST');wd.wait_for_timeout(500);rd=last()
    ok('obs-ws: request is obs-browser emit_event with event_name cfo-state',rd['vendorName']=='obs-browser' and rd['requestType']=='emit_event' and rd['requestData']['event_name']=='cfo-state')
    ok('obs-ws: payload carries the new title',rd['requestData']['event_data']['state']['ev']['title']=='ABC TEST')
    deliver(rd);wo.wait_for_timeout(300);ok('obs-ws: overlay shows CROSSFIT OPEN -> ABC TEST',ev(wo,'S.ev.title')=='ABC TEST' and ev(wo,"ovHTML().includes('ABC')"))
    wd.click('#start');wd.wait_for_timeout(1200);rd=last();deliver(rd);wo.wait_for_timeout(300);t=rd['requestData']['event_data']['timer']
    ok('obs-ws: START payload and overlay timer runs',t['action']=='START' and t['run'] and ev(wo,'S.T.run')==True)
    wd.wait_for_timeout(1500);ok('obs-ws: overlay timer counts down',ev(wo,'disp().mm')=='04' and int(ev(wo,'disp().ss'))<59)
    wd.click('#pause');wd.wait_for_timeout(500);rd=last();deliver(rd);wo.wait_for_timeout(300);ok('obs-ws: PAUSE reaches overlay, times match',rd['requestData']['event_data']['timer']['action']=='PAUSE' and ev(wo,'S.T.run')==False and abs(ev(wo,'el()')-ev(wd,'el()'))<.05)
    wd.click('#reset');wd.wait_for_timeout(500);rd=last();deliver(rd);wo.wait_for_timeout(300);ok('obs-ws: RESET returns overlay to 05:00',ev(wo,'disp().mm+":"+disp().ss')=='05:00')
    wd.wait_for_timeout(2300);n1=len([1 for l in open(ml) if '"request"' in l]);wd.wait_for_timeout(2300);n2=len([1 for l in open(ml) if '"request"' in l])
    ok('obs-ws: heartbeat re-sends state every ~2 s (lets a refreshed OBS source recover)',n2>n1)
    ok('debug logs contain STATE SENT and STATE RECEIVED',any(l.startswith('STATE SENT') for l in wlogs) and any(l.startswith('STATE RECEIVED') for l in wlogs),wlogs[:3])
    mock.terminate()
    # --- unlinked-dashboard warning (screenshot scenario: Chrome dashboard, OBS cannot see it) ---
    wc=ctx(1650,940).new_page();wc.goto(FU);wc.wait_for_timeout(500);wc.fill('[data-k="ev.title"]','ABC TEST');wc.wait_for_timeout(300)
    ok('dashboard warns that OBS cannot see changes when nothing is connected',wc.evaluate("document.querySelector('#msg').textContent.includes('OBS cannot see')"))
    ov2=ctx(1920,1080).new_page();ov2.goto(FU+'#/overlay');ov2.wait_for_timeout(700)
    ok('screenshot scenario reproduced: separate-profile overlay stays at defaults (CROSSFIT OPEN, 05:00)',ev(ov2,'S.ev.title')=='CROSSFIT OPEN' and ev(ov2,'disp().mm+":"+disp().ss')=='05:00')
    # NOTE: Playwright's sync API only runs the exposed host-write callback while a Playwright call is waiting, so waits use wait_for_timeout.
    # --- state-file bridge: Chrome dashboard -> separate-process overlay via state.js (file picker mocked, disk write real) ---
    import tempfile,shutil
    td=tempfile.mkdtemp();shutil.copy(os.path.join(ROOT,'index.html'),td);shutil.copy(os.path.join(ROOT,'state.js'),td)
    TU='file://'+os.path.join(td,'index.html')
    def hostWrite(t):open(os.path.join(td,'state.js'),'w').write(t)
    dpg=ctx(1650,940).new_page();opg=ctx(1920,1080).new_page()
    dpg.expose_function('hostWrite',hostWrite)
    dpg.add_init_script("window.showSaveFilePicker=async()=>({createWritable:async()=>{let b='';return{write:async t=>{b+=t},close:async()=>{await window.hostWrite(b)}}}})")
    dpg.goto(TU);opg.goto(TU+'#/overlay');dpg.wait_for_timeout(800)
    dpg.fill('[data-k="ev.title"]','TEST');dpg.click('[data-t="5"]');dpg.click('#fbtn');dpg.wait_for_timeout(800)
    ok('bridge: linking writes state.js',open(os.path.join(td,'state.js')).read().startswith('window.__CFO='))
    dpg.click('[data-t="0"]');dpg.fill('[data-k="ev.title"]','CROSSFIT CHAMPIONSHIP');dpg.wait_for_timeout(1400)
    ok('bridge: title TEST -> CROSSFIT CHAMPIONSHIP reaches overlay in separate browser context, no refresh',ev(opg,'S.ev.title')=='CROSSFIT CHAMPIONSHIP' and ev(opg,"ovHTML().includes('CHAMPIONSHIP')"),ev(opg,'S.ev.title'))
    dpg.fill('[data-k="ev.sub"]','S2');dpg.fill('[data-k="ev.tag"]','T2');dpg.fill('[data-k="ev.loc"]','L2');dpg.fill('[data-k="ev.date"]','D2');dpg.fill('[data-k="wod.title"]','W2');dpg.fill('[data-k="wod.coach"]','C2');dpg.fill('[data-k="wod.notes"]','N2');dpg.click('#add')
    dpg.click('[data-m=intervals]');dpg.fill('[data-k="tm.wm"]','3');dpg.fill('[data-k="tm.rs"]','20');dpg.fill('[data-k="tm.rounds"]','6');dpg.uncheck('[data-k="st.show.coach"]');dpg.wait_for_timeout(1400)
    ok('bridge: remaining text, WOD, timer settings and visibility sync',ev(opg,"['S2','T2','L2','D2','W2','N2'].every(x=>ovHTML().includes(x))&&S.wod.rows.length==4&&[S.tm.mode,S.tm.wm,S.tm.rs,S.tm.rounds].join()=='intervals,3,20,6'&&!ovHTML().includes('COACH')"))
    dpg.set_input_files('#file',files=[{'name':'l.png','mimeType':'image/png','buffer':buf.getvalue()}]);dpg.wait_for_timeout(1400);ok('bridge: logo upload syncs',ev(opg,'S.logo').startswith('data:image/png'))
    dpg.click('#rm');dpg.wait_for_timeout(1200);ok('bridge: logo removal syncs',ev(opg,'S.logo')=='')
    dpg.click('#start');dpg.wait_for_timeout(1500);ok('bridge: START action broadcast with mode/rounds/elapsed',('"action":"START"' in open(os.path.join(td,'state.js')).read()) and ('"mode":"intervals"' in open(os.path.join(td,'state.js')).read()) and ('"rounds":6' in open(os.path.join(td,'state.js')).read()))
    ok('bridge: timer start syncs and runs on overlay',ev(opg,'S.T.run')==True and ev(opg,'el()')>0.5,ev(opg,'el()'))
    dpg.click('#pause');dpg.wait_for_timeout(1200);ok('bridge: PAUSE action broadcast',('"action":"PAUSE"' in open(os.path.join(td,'state.js')).read()) and ('"run":false' in open(os.path.join(td,'state.js')).read()))
    ok('bridge: pause syncs',ev(opg,'S.T.run')==False and abs(ev(opg,'el()')-ev(dpg,'el()'))<.2)
    dpg.click('#pause');dpg.wait_for_timeout(1200);ok('bridge: RESUME action broadcast and overlay runs again',('"action":"RESUME"' in open(os.path.join(td,'state.js')).read()) and ev(opg,'S.T.run')==True)
    dpg.click('#reset');dpg.wait_for_timeout(1200);ok('bridge: RESET action broadcast',('"action":"RESET"' in open(os.path.join(td,'state.js')).read()) and ('"elapsed":0' in open(os.path.join(td,'state.js')).read()))
    ok('bridge: reset syncs',ev(opg,'el()')==0)
    opg.reload();dpg.wait_for_timeout(1200);ok('bridge: overlay refresh recovers current state from state.js',ev(opg,'S.ev.title')=='CROSSFIT CHAMPIONSHIP')
    br.close()
finally:
    srv.terminate()

# --- stable session across server restarts ---
import tempfile as _t,shutil as _s,re as _r
sd=_t.mkdtemp();_s.copy(os.path.join(ROOT,'server.js'),sd);_s.copy(os.path.join(ROOT,'index.html'),sd)
def _url():
    pr=subprocess.Popen(['node','server.js'],cwd=sd,env={k:v for k,v in os.environ.items() if k not in('SESSION_ID','SESSION_KEY')}|{'PORT':'8097'},stdout=subprocess.PIPE,text=True);time.sleep(1);pr.terminate();o=pr.stdout.read();return _r.search(r'Control URL: (\S+)',o).group(1)
u1,u2=_url(),_url();ok('server keeps the same session URLs after a restart',u1==u2,(u1,u2))
print('\n'.join(R));print(f'{sum(r.startswith("PASS") for r in R)} passed, {sum(r.startswith("FAIL") for r in R)} failed')

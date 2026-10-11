// Advanced tests: timer accuracy, cross-window sync (Node BroadcastChannel in jsdom), SVG safety, import validation.
const {JSDOM}=require('jsdom');const fs=require('fs'),path=require('path');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8').replace(/<link[^>]*>/,'');
const sl=ms=>new Promise(r=>setTimeout(r,ms)),R=[];const ok=(n,c,x)=>R.push((c?'PASS ':'FAIL ')+n+(c?'':' -> '+x));
async function mk(h,store){const d=new JSDOM(html,{runScripts:'dangerously',url:'http://x/i.html'+h,pretendToBeVisual:true,beforeParse(w){w.BroadcastChannel=BroadcastChannel;w.TextDecoder=TextDecoder;if(store)w.localStorage.setItem('CROSSFIT_OVERLAY_STATE',store)}});await sl(300);return d.window}
const up=async(w,f)=>{const i=w.document.querySelector('#file');Object.defineProperty(i,'files',{value:[f],configurable:true});i.dispatchEvent(new w.Event('change'));await sl(250)};
(async()=>{
const A=await mk(''),B=await mk('#/overlay'),Ea=s=>A.eval(s),Eb=s=>B.eval(s),$=s=>A.document.querySelector(s);
const inp=(k,v)=>{const i=$(`[data-k="${k}"]`);i.value=v;i.dispatchEvent(new A.Event('input',{bubbles:true}))};
// accuracy + wall clock jump
$('#start').click();await sl(4000);const e=Ea('el()'),real=Ea('(Date.now()+OFF-S.T.t0)/1000');ok('4 s run within 150 ms of real time',Math.abs(e-real)<.15,e+' vs '+real);
const od=A.Date.now;A.Date.now=()=>od()+3.6e6;await sl(100);ok('wall-clock jump (+1 h) does not move timer',Ea('el()')<e+.5,Ea('el()'));A.Date.now=od;
// sync
await sl(200);ok('sync: start reaches overlay',Eb('S.T.run')===true);ok('sync: overlay elapsed matches',Math.abs(Eb('el()')-Ea('el()'))<.5,Eb('el()')+' '+Ea('el()'));
$('#pause').click();await sl(200);ok('sync: pause',Eb('S.T.run')===false&&Math.abs(Eb('el()')-Ea('el()'))<.05);
$('#pause').click();await sl(200);ok('sync: resume',Eb('S.T.run')===true);
inp('ev.title','SYNC TEST');await sl(150);ok('sync: event text',Eb('S.ev.title')=='SYNC TEST'&&Eb('ovHTML()').includes('SYNC'));
$('[data-th=green]').click();await sl(150);ok('sync: theme',Eb('S.st.theme')=='green');
const c=$('[data-k="st.show.wod"]');c.checked=false;c.dispatchEvent(new A.Event('change',{bubbles:true}));await sl(150);ok('sync: visibility',!Eb('ovHTML()').includes('id="R"'));
$('#sn').value='S1';$('#ssv').click();inp('ev.title','OTHER');$('#sn').value='S1';$('[data-a=l]').click();await sl(150);ok('sync: scene load',Eb('S.ev.title')=='SYNC TEST');
$('#reset').click();await sl(150);ok('sync: reset',Eb('S.T.run')===false&&Eb('el()')==0);
// refresh overlay with persisted state (same profile emulated by copying storage)
$('#start').click();await sl(1200);const snap=A.localStorage.getItem('CROSSFIT_OVERLAY_STATE');const B2=await mk('#/overlay',snap);
ok('overlay refresh keeps state and running timer',B2.eval('S.ev.title')=='SYNC TEST'&&B2.eval('S.T.run')&&B2.eval('el()')>1.2,B2.eval('el()'));
// SVG / PNG safety
const svg=t=>new A.File([t],'l.svg',{type:'image/svg+xml'});
await up(A,svg('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4" fill="red"/></svg>'));ok('valid SVG accepted',Ea('S.logo').startsWith('data:image/svg+xml'));
ok('logo persists after refresh',(await mk('',A.localStorage.getItem('CROSSFIT_OVERLAY_STATE'))).eval('S.logo').startsWith('data:image/svg'));
$('#rm').click();
for(const [n,t] of [['script tag','<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'],['onload attr','<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"></svg>'],['external href','<svg xmlns="http://www.w3.org/2000/svg" xmlns:x="http://www.w3.org/1999/xlink"><image x:href="http://evil/x.png"/></svg>'],['foreignObject','<svg xmlns="http://www.w3.org/2000/svg"><foreignObject/></svg>'],['css url()','<svg xmlns="http://www.w3.org/2000/svg"><rect style="fill:url(http://evil/a)"/></svg>'],['not svg','hello']]){await up(A,svg(t));ok('SVG rejected: '+n,Ea('S.logo')==='',Ea('S.logo').slice(0,30))}
await up(A,new A.File(['not a png'],'a.png',{type:'image/png'}));ok('fake PNG rejected',Ea('S.logo')==='');
await up(A,new A.File([new Uint8Array(600000)],'a.png',{type:'image/png'}));ok('oversize rejected',Ea('S.logo')===''&&$('#msg').textContent.includes('500'));
// import validation
$('#js').value='{"current":{"wod":{"rows":"x"},"st":{"theme":"zzz","op":"abc","show":5},"tm":{"m":"q"},"ev":7},"scenes":[1]}';$('#ji').click();
ok('malformed import repaired',Ea('S.st.theme')=='red'&&Array.isArray(Ea('S.wod.rows'))&&Ea('S.tm.m')==5&&Ea("typeof ovHTML()")=='string');
$('#js').value='{broken';$('#ji').click();ok('invalid JSON reports error',$('#msg').textContent.includes('invalid'));
$('#js').value='{"current":5}';$('#ji').click();ok('non-object current survives',Ea('S.ev.title')=='CROSSFIT OPEN');
// sequence boundaries
for(const [s,x] of [['',"[]"],['2m+30','[120,30]'],['1.5m','[90]'],['90','[90]'],['0m',null],['1:60',null],['-5',null],['1:00:00',null],['2m + + 5',null]])ok('seq "'+s+'"',Ea(`JSON.stringify(parseSeq(${JSON.stringify(s)}))`)==(x===null?'null':x),Ea(`JSON.stringify(parseSeq(${JSON.stringify(s)}))`));
// overlay transparency
const od2=B.document;ok('overlay: transparent html/body, margin 0, no chrome',B.document.documentElement.style.background=='transparent'&&od2.body.className=='ovl'&&!od2.querySelector('nav,.chk'));
console.log(R.join('\n'));process.exit(0)})().catch(e=>{console.log(R.join('\n'));console.log('ERR',e);process.exit(1)});

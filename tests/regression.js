const {JSDOM}=require('jsdom');const fs=require('fs');
const html=fs.readFileSync('/mnt/user-data/outputs/crossfit-overlay-handover/index.html','utf8').replace(/<link[^>]*>/,'');
const sl=ms=>new Promise(r=>setTimeout(r,ms));
const R=[];const ok=(n,c,x)=>R.push((c?'PASS ':'FAIL ')+n+(c?'':' -> '+x));
async function mk(h){const d=new JSDOM(html,{runScripts:'dangerously',url:'http://x/i.html'+h,pretendToBeVisual:true});await sl(300);return d.window}
(async()=>{
let w=await mk('');const D=w.document,E=s=>w.eval(s),$=s=>D.querySelector(s),clk=s=>$(s).click();
const inp=(k,v)=>{const i=$(`[data-k="${k}"]`);i.value=v;i.dispatchEvent(new w.Event('input',{bubbles:true}))};
const chk=(k,v)=>{const i=$(`[data-k="${k}"]`);i.checked=v;i.dispatchEvent(new w.Event('change',{bubbles:true}))};
// timer countdown
clk('#start');await sl(1100);let d=E('disp()');ok('countdown runs 04:5x',d.mm=='04'&&+d.ss<=58&&+d.ss>=57,JSON.stringify(d));
clk('#pause');let a=E('el()');await sl(500);ok('pause freezes',E('el()')==a);
clk('#pause');await sl(400);ok('resume continues',E('el()')>a+.3);
clk('#reset');ok('reset',E('el()')==0&&!E('S.T.run')&&E('disp().mm')=='05');
// stopwatch
$('[data-m=stopwatch]').click();clk('#start');await sl(1100);ok('stopwatch counts up',E('disp().lab')=='STOPWATCH'&&E('disp().ss')=='01',E('JSON.stringify(disp())'));clk('#reset');
// countdown finish
$('[data-m=countdown]').click();inp('tm.m',0);inp('tm.s',1);clk('#start');await sl(1500);ok('countdown completes & stops',!E('S.T.run')&&E('disp().done'),E('JSON.stringify([S.T,disp()])'));
clk('#start');ok('start after done restarts',E('S.T.run')&&!E('disp().done'));clk('#reset');
inp('tm.m',5);inp('tm.s',0);
// intervals
$('[data-m=intervals]').click();inp('tm.wm',0);inp('tm.ws',2);inp('tm.rm',0);inp('tm.rs',1);inp('tm.rounds',2);
const at=s=>{E(`S.T={run:false,acc:${s*1000},t0:0}`);return E('disp()')};
let x=at(1);ok('int work r1',x.ph=='WORK'&&x.rd==1&&x.tot==2&&x.ss=='01',JSON.stringify(x));
x=at(2.5);ok('int rest r1',x.ph=='REST'&&x.rd==1,JSON.stringify(x));
x=at(3.5);ok('int work r2',x.ph=='WORK'&&x.rd==2,JSON.stringify(x));
x=at(6.2);ok('int done',x.done,JSON.stringify(x));
// sequence
ok('seq parse',E("JSON.stringify(parseSeq('2m + 30 + 1:00'))")=='[120,30,60]');
ok('seq invalid',E("parseSeq('abc')")===null&&E("parseSeq('0')")===null&&E("parseSeq('1:99')")===null);
$('#seq').value='3 + 2';clk('#seqa');x=at(3.5);ok('seq applied',E('S.tm.seq')=='3 + 2'&&x.ph=='REST',JSON.stringify(x));$('#seq').value='';clk('#seqa');
$('[data-m=countdown]').click();
// text edits
inp('ev.title','HERO WOD');inp('ev.sub','SUB X');inp('ev.tag','TAG X');inp('ev.loc','Paris');inp('ev.date','May 1');
let h=E('ovHTML()');ok('event text live',['HERO','SUB X','TAG X','Paris','May 1'].every(s=>h.includes(s)));
inp('wod.title','EMOM 9');inp('wod.coach','Sam');inp('wod.notes','A|B');h=E('ovHTML()');ok('wod/coach/notes live',['EMOM 9','Sam','>A<'].every(s=>h.includes(s)),'');
// rows
clk('#add');ok('add row',E('S.wod.rows.length')==4);
let ri=D.querySelectorAll('[data-r="3"]');ri[0].value='30';ri[0].dispatchEvent(new w.Event('input'));ri[1].value='Sit-ups';ri[1].dispatchEvent(new w.Event('input'));ok('edit row',E('S.wod.rows[3].join()')=='30,Sit-ups');
D.querySelector('[data-mv="3"][data-d="-1"]').click();ok('reorder',E('S.wod.rows[2][1]')=='Sit-ups');
D.querySelector('[data-rm="2"]').click();ok('delete row',E('S.wod.rows.length')==3&&!E('ovHTML()').includes('Sit-ups'));
// theme/opacity/toggles/font
$('[data-th=blue]').click();ok('theme',w.document.documentElement.style.getPropertyValue('--a')=='#1e6bff');
inp('st.op',50);ok('opacity',E('ovHTML()').includes('opacity:0.5'));
inp('st.font','Anton');ok('font',E('ovHTML()').includes("'Anton'"));
for(const k of ['logo','event','timer','wod','coach','notes','clock','loc','date','wr']){chk('st.show.'+k,false);}
h=E('ovHTML()');ok('toggles hide all',!h.includes('id="L"')&&!h.includes('class="C"')&&!h.includes('id="R"')&&!h.includes('id="LV"')&&!h.includes('id="W"'));
for(const k of ['logo','event','timer','wod','coach','notes','clock','loc','date','wr'])chk('st.show.'+k,true);
// logo
const f=new w.File([new Uint8Array([137,80,78,71,13,10,26,10])],'a.png',{type:'image/png'});const fi=$('#file');Object.defineProperty(fi,'files',{value:[f],configurable:true});fi.dispatchEvent(new w.Event('change'));await sl(200);
ok('logo upload',E('S.logo').startsWith('data:image/png')&&E('ovHTML()').includes('<img'));
clk('#rm');ok('logo remove',E('S.logo')==''&&!E('ovHTML()').includes('<img'));
Object.defineProperty(fi,'files',{value:[new w.File(['x'],'a.gif',{type:'image/gif'})],configurable:true});fi.dispatchEvent(new w.Event('change'));ok('bad type rejected',E('S.logo')==''&&$('#msg').textContent.includes('PNG'));
// scenes
$('#sn').value='A';clk('#ssv');inp('ev.title','CHANGED');$('#sn').value='A';clk('[data-a=l]');ok('scene save/load',E('S.ev.title')=='HERO WOD',E('S.ev.title'));
clk('[data-a=d]');ok('scene duplicate',Object.keys(JSON.parse(w.localStorage.cfo_scenes_v1)).length==2);
$('#sn').value='B';clk('[data-a=r]');ok('scene rename','B' in JSON.parse(w.localStorage.cfo_scenes_v1),w.localStorage.cfo_scenes_v1.slice(0,80));
clk('[data-a=x]');ok('scene delete',Object.keys(JSON.parse(w.localStorage.cfo_scenes_v1)).length==1);
clk('#jx');const J=JSON.parse($('#js').value);ok('export json',!!J.current&&!!J.scenes);
J.current.ev.title='IMPORTED';$('#js').value=JSON.stringify(J);clk('#ji');ok('import',E('S.ev.title')=='IMPORTED');
clk('#defs');ok('restore defaults',E('S.ev.title')=='CROSSFIT OPEN');
// keyboard
w.dispatchEvent(new w.KeyboardEvent('keydown',{code:'Space'}));ok('space start',E('S.T.run'));w.dispatchEvent(new w.KeyboardEvent('keydown',{code:'Space'}));ok('space pause',!E('S.T.run'));w.dispatchEvent(new w.KeyboardEvent('keydown',{key:'r'}));ok('r reset',E('el()')==0);
// persistence
const w2=await mk('');
// overlay page
const o=await mk('#/overlay');ok('overlay page: no dashboard/checker',!o.document.querySelector('nav')&&!o.document.querySelector('.chk')&&o.document.body.classList.contains('ovl')&&o.document.documentElement.style.background=='transparent');
ok('overlay renders zones',['id="L"','class="C"','id="R"'].every(s=>o.document.querySelector('#strip').innerHTML.includes(s)));
console.log(R.join('\n'));process.exit(0)})().catch(e=>{console.log(R.join('\n'));console.log('ERR',e);process.exit(1)});

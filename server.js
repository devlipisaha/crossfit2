// Optional zero-dependency server: serves index.html and relays one shared session (state sync for OBS / phone / dashboard).
// Run: SESSION_ID=abc SESSION_KEY=secret node server.js   (if unset, values are generated once and stored in .session.json)
const http=require('http'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const PORT=+process.env.PORT||8080,HOST=process.env.HOST||'0.0.0.0';
// Session id/key: environment variables win; otherwise they are created once and kept in .session.json so the URLs stay the same after a restart.
const SF=path.join(__dirname,'.session.json');let saved={};try{saved=JSON.parse(fs.readFileSync(SF,'utf8'))}catch{}
const SID=process.env.SESSION_ID||saved.id||crypto.randomBytes(8).toString('hex'),KEY=process.env.SESSION_KEY||saved.key||crypto.randomBytes(16).toString('hex');
if(!process.env.SESSION_ID&&!process.env.SESSION_KEY&&(saved.id!==SID||saved.key!==KEY)){try{fs.writeFileSync(SF,JSON.stringify({id:SID,key:KEY}),{mode:0o600})}catch{}}
let state=null;const clients=new Set();
const eq=(a,b)=>{a=Buffer.from(String(a||''));b=Buffer.from(String(b||''));return a.length===b.length&&crypto.timingSafeEqual(a,b)};
const send=(res,m)=>res.write('data: '+JSON.stringify(m)+'\n\n');
const srv=http.createServer((q,r)=>{
  const u=new URL(q.url,'http://x'),H={'x-content-type-options':'nosniff','referrer-policy':'no-referrer'};
  if(u.pathname==='/'||u.pathname==='/index.html'){r.writeHead(200,{...H,'content-type':'text/html; charset=utf-8','cache-control':'no-cache'});return fs.createReadStream(path.join(__dirname,'index.html')).pipe(r)}
  if(u.pathname==='/api/events'&&q.method==='GET'){
    if(!eq(u.searchParams.get('s'),SID)){r.writeHead(403,H);return r.end()}
    r.writeHead(200,{...H,'content-type':'text/event-stream','cache-control':'no-cache',connection:'keep-alive'});
    send(r,{from:'',state,t:Date.now()});clients.add(r);const ka=setInterval(()=>r.write(':\n\n'),20000);
    q.on('close',()=>{clients.delete(r);clearInterval(ka)});return}
  if(u.pathname==='/api/time'){r.writeHead(200,{...H,'content-type':'application/json','cache-control':'no-store'});return r.end(JSON.stringify({t:Date.now()}))}
  if(u.pathname==='/api/state'&&q.method==='PUT'){
    if(!eq(u.searchParams.get('s'),SID)||!eq(q.headers['x-key'],KEY)){r.writeHead(403,H);return r.end()}
    let b='',big=false;q.on('data',c=>{b+=c;if(b.length>2e6){big=true;q.destroy()}});
    q.on('end',()=>{if(big)return;try{const m=JSON.parse(b);if(!m||typeof m.state!=='object'||m.state===null)throw 0;state=m.state;
      for(const c of clients)send(c,{from:String(m.from||'').slice(0,40),state,t:Date.now()});r.writeHead(204,H);r.end()}catch{r.writeHead(400,H);r.end()}});return}
  r.writeHead(404,H);r.end()});
srv.listen(PORT,HOST,()=>{console.log(`Server on http://${HOST}:${PORT}\nSession ID : ${SID}\nControl URL: http://localhost:${PORT}/?s=${SID}&k=${KEY}\nOverlay URL (OBS, read-only): http://localhost:${PORT}/?s=${SID}#/overlay`)});
module.exports=srv;

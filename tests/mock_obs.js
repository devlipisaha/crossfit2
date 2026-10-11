// Test double for the OBS WebSocket server (obs-websocket v5 protocol: hello, identify with auth, requests). Logs what the dashboard sends.
// It cannot reproduce OBS's real delivery into browser sources; tests simulate that step with a CustomEvent.
const {WebSocketServer}=require('ws'),crypto=require('crypto'),fs=require('fs');
const PW='secret',port=+process.argv[2],log=process.argv[3],salt='salt123',chal='chal456';
const sha=s=>crypto.createHash('sha256').update(s).digest('base64'),w=o=>fs.appendFileSync(log,JSON.stringify(o)+'\n');
new WebSocketServer({port,host:'127.0.0.1'}).on('connection',ws=>{
  ws.send(JSON.stringify({op:0,d:{obsWebSocketVersion:'5.5.0',rpcVersion:1,authentication:{challenge:chal,salt}}}));
  ws.on('message',m=>{const j=JSON.parse(m);
    if(j.op===1){const ok=j.d.authentication===sha(sha(PW+salt)+chal);w({type:'identify',ok});ok?ws.send(JSON.stringify({op:2,d:{negotiatedRpcVersion:1}})):ws.close(4009)}
    if(j.op===6){w({type:'request',d:j.d});ws.send(JSON.stringify({op:7,d:{requestType:j.d.requestType,requestId:j.d.requestId,requestStatus:{result:true,code:100},responseData:{}}}))}});
});

const path=require('path'), fs=require('fs');
const puppeteer=require('/Users/cns/.nvm/versions/node/v22.19.0/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer');
const DEMO=__dirname;
(async()=>{
  const narr=JSON.parse(fs.readFileSync(path.join(DEMO,'narration.json'),'utf8'));
  const N=narr.length;
  const outDir=path.join(DEMO,'slides'); fs.rmSync(outDir,{recursive:true,force:true}); fs.mkdirSync(outDir,{recursive:true});
  const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--no-sandbox']});
  const pg=await b.newPage();
  await pg.setViewport({width:1920,height:1080,deviceScaleFactor:1});
  await pg.goto('file://'+path.join(DEMO,'demo-deck.html'),{waitUntil:'networkidle0'});
  await new Promise(r=>setTimeout(r,800));
  const hasGoto=await pg.evaluate(()=>typeof window.__goto==='function');
  for(let i=0;i<N;i++){
    if(hasGoto){ await pg.evaluate(n=>window.__goto(n),i); }
    else if(i>0){ await pg.keyboard.press('ArrowRight'); }
    await new Promise(r=>setTimeout(r,450));
    const n=String(i+1).padStart(2,'0');
    await pg.screenshot({path:path.join(outDir,`s${n}.png`)});
    process.stdout.write(`s${n} `);
  }
  await b.close();
  console.log('\nrendered '+N+' slides (nav: '+(hasGoto?'__goto':'ArrowRight')+')');
})().catch(e=>{console.error('RENDER FAIL',e.stack||e.message);process.exit(1)});

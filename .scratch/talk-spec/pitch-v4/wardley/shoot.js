const path=require('path'), fs=require('fs');
const puppeteer=require('/Users/cns/.nvm/versions/node/v22.19.0/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer');
const HERE=__dirname;
(async()=>{
  const specs=JSON.parse(fs.readFileSync(path.join(HERE,'maps.json'),'utf8'));
  const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--no-sandbox']});
  const pg=await b.newPage();
  await pg.setViewport({width:1920,height:1080,deviceScaleFactor:1});
  await pg.goto('file://'+path.join(HERE,'render-map.html'),{waitUntil:'networkidle0'});
  for(const spec of specs){
    await pg.evaluate(s=>window.__draw(s), spec);
    await new Promise(r=>setTimeout(r,220));
    await pg.screenshot({path:path.join(HERE,spec.out)});
    process.stdout.write(spec.out+' ');
  }
  await b.close();
  console.log('\ndone');
})().catch(e=>{console.error('FAIL',e.stack||e.message);process.exit(1)});

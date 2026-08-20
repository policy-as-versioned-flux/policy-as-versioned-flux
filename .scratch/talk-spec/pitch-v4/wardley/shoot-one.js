const path=require('path');
const puppeteer=require('/Users/cns/.nvm/versions/node/v22.19.0/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer');
(async()=>{
  const [,,src,out]=process.argv;
  const b=await puppeteer.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--no-sandbox']});
  const pg=await b.newPage();
  await pg.setViewport({width:1920,height:1080,deviceScaleFactor:1});
  await pg.goto('file://'+path.resolve(src),{waitUntil:'networkidle0'});
  await new Promise(r=>setTimeout(r,300));
  await pg.screenshot({path:out});
  await b.close(); console.log('shot '+out);
})().catch(e=>{console.error(e.message);process.exit(1)});

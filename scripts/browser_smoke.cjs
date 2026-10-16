if(!process.env.DEMO_PASSWORD)throw Error('Configure DEMO_PASSWORD para o teste demo');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:800}});
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 await page.goto((process.env.BROWSER_TEST_URL||'http://127.0.0.1:8000'));
 await page.locator('#username').fill('cliente1988');await page.locator('#password').fill(process.env.DEMO_PASSWORD);await page.locator('#signin').click();
 await page.locator('#workspace').waitFor({state:'visible'});
 await page.locator('#message').fill('Quais soluções de pagamento a Getnet oferece?');await page.locator('#submit').click();
 await page.locator('#messages .bubble').nth(1).waitFor();
 await page.locator('#submit').waitFor({state:'visible'});
 await page.waitForFunction(()=>!document.querySelector('#submit').disabled);
 await page.locator('#message').fill('Como faço para contratar essa solução?');await page.locator('#submit').click();
 await page.waitForFunction(()=>!document.querySelector('#submit').disabled);
 if(!(await page.locator('#messages').innerText()).match(/qual|refere|solução|produto/i))throw Error('Missing follow-up response');

 await page.waitForFunction(()=>!document.querySelector('#submit').disabled);
 await page.locator('#message').fill('Quero atendimento humano');await page.locator('#submit').click();
 await page.locator('.ticket').first().waitFor();
 const tid=(await page.locator('.ticket').first().textContent()).split(' · ')[0];
 const op=await browser.newPage();await op.goto((process.env.BROWSER_TEST_URL||'http://127.0.0.1:8000'));await op.locator('#username').fill('operador');await op.locator('#password').fill(process.env.DEMO_PASSWORD);await op.locator('#signin').click();await op.getByRole('button',{name:'Assumir'}).first().click();
 await op.locator('.ticket textarea').first().fill('Atendimento humano demonstrado no navegador.');
 await op.getByRole('button',{name:'Responder',exact:true}).first().click();await op.getByRole('button',{name:'Fechar',exact:true}).first().waitFor();
 await page.locator('#refresh').click();await page.getByText('Atendimento humano demonstrado no navegador.',{exact:false}).first().waitFor();
 await op.getByRole('button',{name:'Fechar',exact:true}).first().click();
 await page.locator('#refresh').click();await page.getByText('Encerrado',{exact:true}).first().waitFor();
 if(await page.getByRole('button',{name:'Assumir',exact:true}).count())throw Error('Customer sees operator actions');


 await page.setViewportSize({width:390,height:844});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 require('fs').writeFileSync('evidence/browser-report.json',JSON.stringify({login:true,multi_turn:true,ticket_operator_reply:true,customer_update:true,mobile_overflow:overflow,page_errors:errors},null,2));
 if(overflow||errors.length)throw Error('UI errors');
 await browser.close();console.log('Browser E2E passed: login, multi-turn, operator response, customer update, mobile layout.');
})().catch(e=>{console.error(e);process.exit(1)});

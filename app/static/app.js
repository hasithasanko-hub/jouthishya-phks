
// --- PHKS Creation Trial / Paid UI ---
let COMMERCIAL_STATUS={mode:'paid',publisher:'PHKS Creation',whatsapp:'+94715954563',trial_remaining:null};
async function loadCommercialStatus(){
  try{
    const r=await fetch('/api/commercial/status',{cache:'no-store'});
    COMMERCIAL_STATUS=await r.json();
    const b=document.createElement('div');
    b.id='phksCommercialBanner';
    b.style.cssText='position:fixed;right:18px;bottom:18px;z-index:9999;background:#0b1d2d;color:#f7ead2;border:1px solid #c7a25a;border-radius:14px;padding:10px 14px;box-shadow:0 12px 30px rgba(0,0,0,.28);font:600 12px Nirmala UI,Segoe UI,sans-serif;max-width:340px';
    if(COMMERCIAL_STATUS.mode==='trial') b.innerHTML=`<b style="color:#e5bd67">TRIAL VERSION</b> • ඉතිරි කේන්දර ${COMMERCIAL_STATUS.trial_remaining}/${COMMERCIAL_STATUS.trial_limit}<br><span style="font-weight:400">Full version: PHKS Creation • WhatsApp +94 71 595 4563</span>`;
    else b.innerHTML=`<b style="color:#e5bd67">PHKS Creation</b> • ගෙවූ සංස්කරණය<br><span style="font-weight:400">WhatsApp +94 71 595 4563</span>`;
    document.body.appendChild(b);
  }catch(e){}
}
window.addEventListener('DOMContentLoaded',loadCommercialStatus);
function trialWatermarkHtml(){return COMMERCIAL_STATUS.mode==='trial'?`<div style="position:fixed;inset:42% 0 auto 0;text-align:center;transform:rotate(-28deg);font:900 42px Arial;color:rgba(120,20,40,.10);z-index:999999;pointer-events:none">TRIAL VERSION • PHKS Creation</div><div style="position:fixed;left:0;right:0;bottom:4mm;text-align:center;font:700 9px Arial;color:#7a2638;z-index:999999">Trial report • PHKS Creation • WhatsApp +94 71 595 4563</div>`:'';}


// v3.3 — SQLite mirror helpers
function dbMirrorSet(key,value){fetch('/api/localdb/set',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key,value})}).catch(()=>{});}
function dbMirrorDelete(key){fetch('/api/localdb/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key})}).catch(()=>{});}
const cities = [["කොළඹ",6.9271,79.8612,5.5],["හම්බන්තොට",6.1241,81.1185,5.5],["මහනුවර",7.2906,80.6337,5.5],["ගාල්ල",6.0329,80.2168,5.5],["මාතර",5.9549,80.5550,5.5],["යාපනය",9.6615,80.0255,5.5],["කුරුණෑගල",7.4863,80.3647,5.5],["අනුරාධපුර",8.3114,80.4037,5.5],["රත්නපුර",6.7056,80.3847,5.5],["බදුල්ල",6.9934,81.0550,5.5],["මඩකලපුව",7.717,81.7,5.5],["ත්‍රිකුණාමලය",8.5874,81.2152,5.5],["මීගමුව",7.2083,79.8358,5.5],["නුවරඑළිය",6.9497,80.7891,5.5],["කළුතර",6.5854,79.9607,5.5],["කෑගල්ල",7.2513,80.3464,5.5],["වෙනත් ස්ථානය",6.9271,79.8612,5.5]];
const SIGNS = ["මේෂ","වෘෂභ","මිථුන","කටක","සිංහ","කන්‍යා","තුලා","වෘශ්චික","ධනු","මකර","කුම්භ","මීන"];
const NAKS = ["අස්විද","බෙරණ","කැති","රෙහෙණ","මුවසිරස","අද","පුනාවස","පුෂ","අස්ලිය","මා","පුවපල්","උත්‍රපල්","හත","සිත","සා","විසා","අනුර","දෙට","මුල","පුවසල","උත්‍රසල","සුවණ","දෙනට","සියාවස","පුවපුටුප","උත්‍රපුටුප","රේවතී"];
const DASHAS = [["Ketu","කේතු"],["Venus","ශුක්‍ර"],["Sun","රවි"],["Moon","චන්ද්‍ර"],["Mars","කුජ"],["Rahu","රාහු"],["Jupiter","ගුරු"],["Saturn","ශනි"],["Mercury","බුධ"]];
const PLANETS = [["Sun","රවි"],["Moon","චන්ද්‍ර"],["Mars","කුජ"],["Mercury","බුධ"],["Jupiter","ගුරු"],["Venus","ශුක්‍ර"],["Saturn","ශනි"],["Rahu","රාහු"],["Ketu","කේතු"]];
const $ = (s)=>document.querySelector(s);
const esc = (s)=>String(s ?? "").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[m]));
function reportCode(prefix='HJ'){const seed=`${prefix}|${new Date().toISOString()}|${Math.random()}`;let h=2166136261;for(let i=0;i<seed.length;i++){h^=seed.charCodeAt(i);h=Math.imul(h,16777619)}return `${prefix}-${new Date().toISOString().slice(0,10).replaceAll('-','')}-${(h>>>0).toString(36).toUpperCase().padStart(7,'0').slice(0,7)}`;}
function reportVerificationHtml(code){return `<div class="verification-card"><div><b>වාර්තා සත්‍යාපන අංකය</b><div class="verification-code">${esc(code)}</div><small>මෙම අංකය ගනුදෙනුකරු ගොනුව සහ සුරැකි වාර්තා සමඟ සසඳා වාර්තාව හඳුනාගැනීමට භාවිතා කරන්න.</small></div><div style="font-size:28px;color:#c7a25a">✦</div></div>`;const pb=byId('clientPrintCurrent');if(pb)pb.onclick=()=>printableWindow('ගනුදෙනුකරු ගොනුව',detail.innerHTML,`${c.name||''} • වාර්තා ${reports.length}`);}

let lastBirthResult = null;
let lastReferenceResult = null;
const DEFAULT_SETTINGS={institute:'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය',astrologer:'',phone:'',address:'',email:'',creator:'PHKS Creation',footer:'මෙම වාර්තාව සාම්ප්‍රදායික ජ්‍යෝතිෂ්‍ය විග්‍රහයකි.',template:'classic',logo:'',signature:'',seal:'',verificationUrl:''};
function getSettings(){try{return {...DEFAULT_SETTINGS,...JSON.parse(localStorage.getItem('jyotishya_settings')||'{}')}}catch(e){return {...DEFAULT_SETTINGS}}}
function applySettings(){const c=getSettings();const hi=document.getElementById('headerInstitute');const ha=document.getElementById('headerAstrologer');if(hi)hi.textContent=c.institute||'හෙළ ජ්‍යෝතිෂ්‍ය පද්ධතිය';if(ha)ha.textContent=c.astrologer?('ජ්‍යෝතිෂ්‍යවේදී: '+c.astrologer):'ජ්‍යෝතිෂ්‍ය ගණිත හා විග්‍රහ පද්ධතිය';}
function translateMethod(m){const map={'Lahiri sidereal ayanamsa':'ලහිරි නිරයන අයනංශය','Whole-sign houses':'සම්පූර්ණ රාශි භාව පද්ධතිය','Vimshottari Maha/Antar Dasha':'විම්ශෝත්තරී මහා සහ අතුරු දශා','Classical graha drishti':'සාම්ප්‍රදායික ග්‍රහ දෘෂ්ටි','D2/D3/D7/D9/D10/D12 vargas':'හෝරා, ද්‍රෙක්කාණ, සප්තාංශ, නවාංශ, දශාංශ, ද්වාදශාංශ වර්ග','Panchanga':'පංචාංග ගණිතය','Current gochara':'වත්මන් ගෝචරය'};return map[m]||m;}


function options(list){return list.map((x,i)=>`<option value="${i}">${x}</option>`).join('')}
function signOptions(){ return SIGNS.map((x,i)=>`<option value="${i}">${x}</option>`).join(''); }
function nakOptions(){ return NAKS.map((x,i)=>`<option value="${i}">${x}</option>`).join(''); }
function dashaOptions(){ return DASHAS.map(([k,v])=>`<option value="${k}">${v}</option>`).join(''); }
function cityOptions(){ return cities.map((c,i)=>`<option value="${i}">${c[0]}</option>`).join(''); }
function setupCitySelect(selId, latId, lonId, tzId, preset=0){
  const sel = document.getElementById(selId); sel.innerHTML = cityOptions(); sel.value = preset;
  const apply = ()=>{ const c = cities[+sel.value]; document.getElementById(latId).value = c[1]; document.getElementById(lonId).value = c[2]; document.getElementById(tzId).value = c[3]; };
  sel.addEventListener('change', apply); apply();
}
setupCitySelect('city','lat','lon','tz',1);
if($('#knownLagna')) $('#knownLagna').innerHTML += signOptions();
if($('#analysisDate') && !$('#analysisDate').value) $('#analysisDate').value = new Date().toISOString().slice(0,10);
setupCitySelect('refCity','refLat','refLon','refTz',1);

$('#refLagna').innerHTML += signOptions();
$('#refMoon').innerHTML += signOptions();
$('#refNak').innerHTML += nakOptions();
$('#refMaha').innerHTML += dashaOptions();
$('#refAntar').innerHTML += dashaOptions();

function miniFields(prefix, title){
  return `<label>නම<input id="${prefix}Name" value="${title}" required></label><label>දිනය<input id="${prefix}Date" type="date" value="1997-03-18" required></label><label>වෙලාව<input id="${prefix}Time" type="time" value="10:20" required></label><label>ස්ථානය<select id="${prefix}City"></select></label><label>අක්ෂාංශය<input id="${prefix}Lat" type="number" step="0.0001" value="6.1241" required></label><label>දේශාංශය<input id="${prefix}Lon" type="number" step="0.0001" value="81.1185" required></label><label>සම්මත වේලා වෙනස<input id="${prefix}Tz" type="number" step="0.5" value="5.5" required></label>`;
}
$('#groomFields').innerHTML = miniFields('groom','පුරුෂ පාර්ශවය'); $('#brideFields').innerHTML = miniFields('bride','ස්ත්‍රී පාර්ශවය'); setupCitySelect('groomCity','groomLat','groomLon','groomTz',1); setupCitySelect('brideCity','brideLat','brideLon','brideTz',1);

function goTab(name){ document.querySelector(`.tab[data-tab="${name}"]`).click(); }
if($('#jumpBirth')) $('#jumpBirth').onclick = ()=>{ goTab('birth'); window.scrollTo({top:0,behavior:'smooth'});} ;
if($('#jumpReference')) $('#jumpReference').onclick = ()=>{ goTab('reference'); window.scrollTo({top:0,behavior:'smooth'});} ;
if($('#jumpMatch')) $('#jumpMatch').onclick = ()=>{ goTab('match'); window.scrollTo({top:0,behavior:'smooth'});} ;

document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active')); btn.classList.add('active');
  const tab = btn.dataset.tab; $('#birthTab').classList.toggle('hidden', tab !== 'birth'); $('#referenceTab').classList.toggle('hidden', tab !== 'reference'); $('#matchTab').classList.toggle('hidden', tab !== 'match');
}));

function mainPayload(){ return {name:$('#name').value, birth_date:$('#date').value, birth_time:$('#time').value, birth_place:$('#city').selectedOptions[0].text, latitude:+$('#lat').value, longitude:+$('#lon').value, timezone_offset:+$('#tz').value, analysis_date:$('#analysisDate')?$('#analysisDate').value:'', known_lagna:$('#knownLagna')?$('#knownLagna').value:''}; }
function payload(prefix){ const g=(id)=>document.getElementById(prefix+id); return {name:g('Name').value,birth_date:g('Date').value,birth_time:g('Time').value,birth_place:g('City').selectedOptions[0].text,latitude:+g('Lat').value,longitude:+g('Lon').value,timezone_offset:+g('Tz').value}; }
function referenceBirthPayload(){
  return {
    name: $('#refName').value,
    birth_date: $('#refDate').value,
    birth_time: $('#refTime').value,
    birth_place: $('#refCity').selectedOptions[0].text,
    latitude: +$('#refLat').value,
    longitude: +$('#refLon').value,
    timezone_offset: +$('#refTz').value
  };
}
function referenceAnchors(){
  const obj = {source_notes: $('#refNotes').value};
  if($('#refLagna').value !== '') obj.lagna_sign_index = +$('#refLagna').value;
  if($('#refMoon').value !== '') obj.moon_sign_index = +$('#refMoon').value;
  if($('#refNak').value !== '') obj.nakshatra_index = +$('#refNak').value;
  if($('#refPada').value !== '') obj.nakshatra_pada = +$('#refPada').value;
  if($('#refMaha').value) obj.current_mahadasha = $('#refMaha').value;
  if($('#refAntar').value) obj.current_antardasha = $('#refAntar').value;
  if($('#refDashaStart').value.trim()) obj.current_dasha_start = $('#refDashaStart').value.trim();
  if($('#refDashaEnd').value.trim()) obj.current_dasha_end = $('#refDashaEnd').value.trim();
  return obj;
}
async function post(url,data){ const res = await fetch(url,{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)}); const json = await res.json().catch(()=>({error:'නොදන්නා ප්‍රතිචාරයක්'})); if(!res.ok) throw new Error(json.error || 'ඉල්ලීම අසාර්ථක විය'); if(COMMERCIAL_STATUS.mode==='trial' && (url==='/api/calculate'||url==='/api/autofill_reference')){fetch('/api/commercial/status',{cache:'no-store'}).then(r=>r.json()).then(x=>{COMMERCIAL_STATUS=x;const b=document.getElementById('phksCommercialBanner');if(b)b.innerHTML=`<b style=\"color:#e5bd67\">TRIAL VERSION</b> • ඉතිරි කේන්දර ${x.trial_remaining}/${x.trial_limit}<br><span style=\"font-weight:400\">Full version: PHKS Creation • WhatsApp +94 71 595 4563</span>`;}).catch(()=>{});} return json; }
function summaryCard(label, main, sub){ return `<div class="summary-card"><div class="eyebrow">${esc(label)}</div><div class="main">${esc(main)}</div><div class="sub">${esc(sub || '')}</div></div>`; }
const chartOrder = [11,0,1,2,10,'center',3,9,4,8,7,6,5];
const PLANET_SHORT={'රවි':'ර','චන්ද්‍ර':'ච','කුජ':'කු','බුධ':'බු','ගුරු':'ගු','ශුක්‍ර':'ශු','ශනි':'ශ','රාහු':'රා','කේතු':'කේ'};
function shortPlanetLabel(label){ const raw=String(label||''); const rx=raw.includes('℞')?' ℞':''; const base=raw.replace('℞','').trim(); return (PLANET_SHORT[base]||base)+rx; }
function chartBox(cell, corner=''){ return `<div class="chart-box traditional-cell ${corner}"><div class="sign-no">${cell.sign_index + 1}</div><div class="sign-name">${esc(cell.sign)}</div><div class="occupants">${cell.planets.length ? cell.planets.map(x=>esc(shortPlanetLabel(x))).join('<br>') : ''}</div></div>`; }
function zodiacImage(signIndex, signName){ const i=((Number(signIndex)||0)%12+12)%12; return `<img class="lagna-zodiac-img" src="/static/zodiac/${i}.svg" alt="${esc(signName||SIGNS[i])}">`; }
function lagnaCenterHtml(lagnaInfo,title){ const li=lagnaInfo||{}; const idx=Number(li.index??0); const nm=li.name||SIGNS[idx]||'—'; const deg=Number(li.degree); return `<div class="lagna-center-inner">${zodiacImage(idx,nm)}<div class="lagna-center-label">ලග්නය</div><strong>${esc(nm)}</strong>${Number.isFinite(deg)?`<span>${deg.toFixed(2)}°</span>`:''}<em>${esc(title)}</em></div>`; }
function squareChart(cells, title, lagnaInfo){ const corners={0:'corner-tl',3:'corner-tr',9:'corner-bl',12:'corner-br'}; let html = `<div class="panel traditional-chart-panel"><div class="panel-head"><h3>${esc(title)}</h3><div class="micro">ශ්‍රී ලංකා සාම්ප්‍රදායික ආකෘතිය</div></div><div class="square-chart sri-lanka-chart">`; chartOrder.forEach((item,pos)=>{ if(item === 'center'){ html += `<div class="chart-center traditional-center">${lagnaCenterHtml(lagnaInfo,title)}</div>`; } else { html += chartBox(cells[item], corners[pos]||''); } }); html += `</div><div class="chart-legend">ග්‍රහ නාම කෙටි අක්ෂරයෙන් • ℞ = වක්‍ර ගමන</div></div>`; return html; }
function housesPanel(houses){ return `<div class="panel"><div class="panel-head"><h3>භාව සාරාංශය</h3><div class="micro">භාව 12</div></div><div class="house-grid">${houses.map(h=>`<div class="house-card"><b>${h.house} වන භාවය</b><small>${esc(h.rashi)} • අධිපති ${esc(h.lord)}</small><div>${h.planets.length ? h.planets.map(p=>`<span class="house-pill">${esc(p)}</span>`).join('') : '<span class="house-pill">ග්‍රහ නොමැත</span>'}</div></div>`).join('')}</div></div>`; }
function planetsTable(planets){ const arr = Object.values(planets); return `<div class="panel"><div class="panel-head"><h3>ග්‍රහ පිහිටීම්</h3><div class="micro">කේන්දර දත්ත</div></div><div class="table-wrap"><table class="planet-table"><thead><tr><th>ග්‍රහයා</th><th>රාශිය</th><th>අංශක</th><th>භාවය</th><th>නැකත</th><th>පාදය</th><th>නවාංශය</th></tr></thead><tbody>${arr.map(x=>`<tr><td><b>${esc(x.name)}</b>${x.retrograde ? ' <span class="rx">වක්‍ර</span>' : ''}</td><td>${esc(x.rashi.name)}</td><td>${Number(x.rashi.degree || 0).toFixed(2)}°</td><td>${x.house || '—'}</td><td>${esc(x.nakshatra?.name || '—')}</td><td>${esc(x.nakshatra?.pada || '—')}</td><td>${esc(x.navamsa?.name || '—')}</td></tr>`).join('')}</tbody></table></div></div>`; }
function readingPanel(reading){ return `<div class="panel"><div class="panel-head"><h3>සම්පූර්ණ කේන්දර විග්‍රහය</h3><div class="micro">විස්තරාත්මක විග්‍රහය</div></div><div class="reading-wrap"><div class="reading-card reading-summary"><h4>ප්‍රධාන සාරාංශය</h4><ul>${reading.summary.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>${reading.sections.map((s,i)=>`<div class="reading-card detailed-reading-card"><div class="reading-index">${String(i+1).padStart(2,'0')}</div><div><h4>${esc(s.title)}</h4><p>${esc(s.text)}</p></div></div>`).join('')}</div></div>`; }
function dashaPanel(dasha){ const rows = (dasha.periods || []).length ? dasha.periods : (dasha.current ? [dasha.current] : []); return `<div class="panel"><div class="panel-head"><h3>දශා / කාල සාරාංශය</h3><div class="micro">කාල සටහන</div></div><div class="dasha-list">${rows.length ? rows.slice(0,9).map(p=>`<div class="dasha-row ${dasha.current && dasha.current.name === p.name ? 'current' : ''}"><b>${esc(p.name)}</b><span>${esc(p.start || '')}</span><span>${esc(p.end || '')}</span></div>`).join('') : '<div class="note">දශා විස්තර ඇතුළත් කර නැත.</div>'}</div>${dasha.antardasha ? `<div class="note">අතුරු දශාව: ${esc(dasha.antardasha)}</div>` : ''}</div>`; }

function advancedPanel(a){
  if(!a) return '';
  const p=a.panchanga||{};
  const panch=`<div class="panel"><div class="panel-head"><h3>පංචාංග ගණිතය</h3><div class="micro">පංචාංගය</div></div><table class="metric-table"><tbody><tr><th>වාරය</th><td>${esc(p.vara||'—')}</td><th>තිථිය</th><td>${esc(p.paksha||'')} ${esc(p.tithi||'—')}</td></tr><tr><th>නැකත</th><td>${esc(p.nakshatra||'—')} / ${esc(p.pada||'—')}</td><th>යෝග</th><td>${esc(p.yoga||'—')}</td></tr><tr><th>කරණ</th><td>${esc(p.karana||'—')}</td><th>අයනාංශ</th><td>${p.ayanamsa??'—'}°</td></tr><tr><th>ජූලියන් දින අංකය</th><td colspan="3">${p.julian_day??'—'}</td></tr></tbody></table></div>`;
  const dign=`<div class="panel"><div class="panel-head"><h3>ග්‍රහ බල / ස්ථාන තත්ත්වය</h3><div class="micro">ග්‍රහ බලය</div></div><table class="metric-table"><thead><tr><th>ග්‍රහයා</th><th>තත්ත්වය</th><th>භාවය</th><th>වර්ගය</th></tr></thead><tbody>${(a.dignity||[]).map(x=>`<tr><td>${esc(x.planet)}</td><td>${esc(x.state)}</td><td>${esc(x.house)}</td><td>${esc(x.house_class)}${x.retrograde?' • වක්‍ර':''}</td></tr>`).join('')}</tbody></table></div>`;
  const yd=a.yoga_dosha||{yogas:[],doshas:[]};
  const yoga=`<div class="panel"><div class="panel-head"><h3>යෝග සහ දෝෂ පරීක්ෂාව</h3><div class="micro">නීති පරීක්ෂාව</div></div><div class="pro-section-label">යෝග</div>${(yd.yogas||[]).map(x=>`<div class="flag-card"><b>${esc(x.name)}</b><br>${esc(x.note)}</div>`).join('')}<div class="pro-section-label" style="margin-top:14px">දෝෂ</div>${(yd.doshas||[]).map(x=>`<div class="flag-card"><b>${esc(x.name)}</b><br>${esc(x.note)}</div>`).join('')}</div>`;
  const go=a.gochara||{rows:[],flags:[]};
  const goch=`<div class="panel"><div class="panel-head"><h3>වත්මන් ගෝචරය</h3><div class="micro">${esc(go.as_of||'')}</div></div><table class="metric-table"><thead><tr><th>ග්‍රහයා</th><th>රාශිය</th><th>චන්ද්‍රයෙන්</th><th>ලග්නයෙන්</th></tr></thead><tbody>${(go.rows||[]).map(x=>`<tr><td>${esc(x.planet)}</td><td>${esc(x.sign)}${x.retrograde?' • වක්‍ර':''}</td><td>${x.from_moon}</td><td>${x.from_lagna}</td></tr>`).join('')}</tbody></table>${(go.flags||[]).map(x=>`<div class="flag-card">${esc(x)}</div>`).join('')}</div>`;
  const ad=a.antardasha||{periods:[]};
  const antar=`<div class="panel"><div class="panel-head"><h3>අතුරු දශා</h3><div class="micro">විම්ශෝත්තරී</div></div><table class="metric-table"><thead><tr><th>අතුරු දශාව</th><th>ආරම්භය</th><th>අවසානය</th></tr></thead><tbody>${(ad.periods||[]).map(x=>`<tr${ad.current&&ad.current.start===x.start?' style="background:#f8f2e6"':''}><td>${esc(x.name)}</td><td>${esc(x.start)}</td><td>${esc(x.end)}</td></tr>`).join('')}</tbody></table></div>`;
  const dr=`<div class="panel"><div class="panel-head"><h3>ග්‍රහ දෘෂ්ටි</h3><div class="micro">ග්‍රහ දෘෂ්ටි</div></div><table class="metric-table"><thead><tr><th>ග්‍රහයා</th><th>සිට</th><th>දෘෂ්ටි රාශි</th></tr></thead><tbody>${(a.drishti||[]).map(x=>`<tr><td>${esc(x.planet)}</td><td>${esc(x.from_sign)}</td><td>${x.targets.map(t=>`${t.aspect}→${esc(t.sign)}`).join(' • ')}</td></tr>`).join('')}</tbody></table></div>`;
  const hf=a.hela_factors||{};
  const houseLords=(hf.house_lords||[]).map(x=>`<tr><td>${x.house}</td><td>${esc(x.sign)}</td><td>${esc(x.lord)}</td><td>${esc(x.lord_house??'—')}</td><td>${esc(x.class)}</td></tr>`).join('');
  const hela=`<div class="panel"><div class="panel-head"><h3>භාව අධිපති සහ හෙළ ජ්‍යෝතිෂ්‍ය පරීක්ෂාව</h3><div class="micro">අධිපති සම්බන්ධතා</div></div><div class="flag-card"><b>ලග්නාධිපති</b><br>${hf.lagna_lord?`${esc(hf.lagna_lord.planet)} • ${esc(hf.lagna_lord.sign)} • ${esc(hf.lagna_lord.house)} වන භාවය`:'—'}</div><div class="flag-card"><b>ජන්ම නැකත් අධිපති</b><br>${hf.nakshatra_lord?`${esc(hf.nakshatra_lord.nakshatra)} • ${esc(hf.nakshatra_lord.planet)} • පාදය ${esc(hf.nakshatra_lord.pada)}`:'—'}</div><div class="pro-section-label" style="margin-top:14px">රාජ යෝග මූලික පරීක්ෂාව</div>${(hf.raja_yoga_reference||[]).map(x=>`<div class="flag-card">${esc(x)}</div>`).join('')}<div class="pro-section-label" style="margin-top:14px">ධන යෝග මූලික පරීක්ෂාව</div>${(hf.dhana_yoga_reference||[]).map(x=>`<div class="flag-card">${esc(x)}</div>`).join('')}<div class="table-wrap" style="margin-top:14px"><table class="metric-table"><thead><tr><th>භාවය</th><th>රාශිය</th><th>අධිපති</th><th>අධිපති සිටින භාවය</th><th>වර්ගය</th></tr></thead><tbody>${houseLords}</tbody></table></div><div class="note">${esc(hf.note||'')}</div></div>`;
  const ps=a.planet_strength||{rows:[]};
  const strength=`<div class="panel"><div class="panel-head"><h3>ග්‍රහ බල සාර දර්ශකය</h3><div class="micro">සාර බලය</div></div><table class="metric-table"><thead><tr><th>ග්‍රහයා</th><th>බල අගය</th><th>තත්ත්වය</th><th>හේතු</th></tr></thead><tbody>${(ps.rows||[]).map(x=>`<tr><td>${esc(x.planet)}</td><td><b>${x.score}/100</b></td><td>${esc(x.level)}</td><td>${(x.reasons||[]).map(esc).join(' • ')}</td></tr>`).join('')}</tbody></table><div class="note">${esc(ps.note||'')}</div></div>`;
  const pr=a.pratyantardasha||{periods:[]};
  const praty=`<div class="panel"><div class="panel-head"><h3>ප්‍රත්‍යන්තර දශා</h3><div class="micro">විම්ශෝත්තරී</div></div><table class="metric-table"><thead><tr><th>ප්‍රත්‍යන්තර දශාව</th><th>ආරම්භය</th><th>අවසානය</th></tr></thead><tbody>${(pr.periods||[]).map(x=>`<tr${pr.current&&pr.current.start===x.start?' style="background:#f8f2e6"':''}><td>${esc(x.name)}</td><td>${esc(x.start)}</td><td>${esc(x.end)}</td></tr>`).join('')}</tbody></table></div>`;
  const mal=`<div class="panel"><div class="panel-head"><h3>ශනි • රාහු • කේතු • කුජ විශේෂ විග්‍රහය</h3><div class="micro">ගැඹුරු සාරාංශය</div></div>${(a.malefic_analysis||[]).map(x=>`<div class="flag-card"><b>${esc(x.planet)} — ${esc(x.level)}</b><br>${(x.points||[]).map(p=>`• ${esc(p)}`).join('<br>')}</div>`).join('')}</div>`;
  const av=a.ashtakavarga||{signs:[],bav:{},checks:{}};
  const ashta=`<div class="panel"><div class="panel-head"><h3>අෂ්ටකවර්ග ගණනය</h3><div class="micro">සර්වාෂ්ටකවර්ග</div></div><div class="ashta-grid">${(av.signs||[]).map(x=>`<div class="ashta-cell"><b>${esc(x.sign)}</b><strong>${esc(x.points)}</strong><span>${esc(x.level)}</span></div>`).join('')}</div><div class="table-wrap" style="margin-top:14px"><table class="metric-table"><thead><tr><th>ග්‍රහයා</th>${SIGNS.map(x=>`<th>${esc(x)}</th>`).join('')}<th>එකතුව</th></tr></thead><tbody>${Object.entries(av.bav||{}).map(([k,row])=>`<tr><td>${esc((PLANETS.find(p=>p[0]===k)||[k,k])[1])}</td>${row.map(v=>`<td>${v}</td>`).join('')}<td><b>${(av.checks&&av.checks[k])?av.checks[k].total:'—'}</b></td></tr>`).join('')}<tr><td><b>සර්වාෂ්ටකවර්ග</b></td>${(av.sav||[]).map(v=>`<td><b>${v}</b></td>`).join('')}<td><b>${av.total||'—'}</b></td></tr></tbody></table></div><div class="note">${esc(av.note||'')}</div></div>`;
  const vargas=a.vargas||{};
  const vg=`<div class="panel"><div class="panel-head"><h3>වර්ග කේන්දර</h3><div class="micro">වර්ග කේන්දර</div></div><div class="varga-tabs">${Object.values(vargas).map(v=>`<span class="varga-chip"><b>${esc(v.code)}</b> ${esc(v.title)} • ලග්න ${esc(v.lagna_sign)}</span>`).join('')}</div><div class="tech-badges">${(a.methods||[]).map(m=>`<span class="tech-badge">${esc(translateMethod(m))}</span>`).join('')}</div></div>`;
  return `<div class="pro-section-label" style="margin-top:22px">උසස් ජ්‍යෝතිෂ්‍ය ගණිත පරීක්ෂණ</div><div class="advanced-grid">${panch}${dign}${strength}${ashta}${yoga}${goch}${antar}${praty}${dr}${mal}${hela}</div><div style="margin-top:14px">${vg}</div>`;
}


function auditPanel(a){
  if(!a) return '';
  const v=a.verification;
  const verify=v ? `<div class="reading-card"><h4>දන්නා ලග්නය සමඟ පරීක්ෂාව</h4><p class="${v.match?'status-good':'status-bad'}">දන්නා ලග්නය: ${esc(v.known)} • ගණනය කළ ලග්නය: ${esc(v.calculated)} • ${v.match?'ගැලපේ':'නොගැලපේ'}</p></div>` : '';
  return `<div class="panel" style="margin-top:18px"><div class="panel-head"><h3>ගණිත සත්‍යාපන වාර්තාව</h3><div class="micro">අභ්‍යන්තර පරීක්ෂාව</div></div><div class="reading-wrap">
    <div class="reading-card"><h4>භාවිත කළ වේලාව</h4><p>UTC: ${esc(a.utc_datetime)}<br>ශ්‍රී ලංකා නීතිමය වේලා වෙනස: UTC ${esc(a.timezone_used)}<br>${a.standard_time_0530_equivalent?`UTC+5:30 සම්මතයට සමාන වේලාව: ${esc(a.standard_time_0530_equivalent)}`:''}</p></div>
    <div class="reading-card"><h4>ලග්න ද්විත්ව පරීක්ෂාව</h4><p>සායන ලග්නය: ${Number(a.tropical_ascendant||0).toFixed(4)}°<br>අයනංශය: ${Number(a.ayanamsa||0).toFixed(4)}°<br>නිරයන පරීක්ෂණ අගය: ${Number(a.sidereal_crosscheck||0).toFixed(4)}°<br>වෙනස: ${Number(a.crosscheck_difference||0).toFixed(6)}°</p></div>
    <div class="reading-card"><h4>ස්ථාවර ගණිත පැතිකඩ</h4><p>${esc(a.calculation_profile_name||'ශ්‍රී ලංකා ස්ථාවර නිරයන ගණිත ක්‍රමය')}<br>අයනංශය: ${esc(a.ayanamsa_name)}<br>රාහු / කේතු: ${esc(a.node_mode)}<br>භාව ක්‍රමය: ${esc(a.house_method)}<br>ජන්ම සත්‍යාපන අංකය: <b>${esc(a.natal_signature||'—')}</b><br>විග්‍රහ දිනය: ${esc(a.analysis_date||'—')}</p></div>${verify}${a.lagna_time_diagnostic?`<div class="reading-card"><h4>ලග්න නොගැලපීමේ පරීක්ෂාව</h4><p>${esc(a.lagna_time_diagnostic.match_window?('දන්නා ලග්නය ලැබෙන ආසන්න වෙලා පරාසය: '+a.lagna_time_diagnostic.match_window):a.lagna_time_diagnostic.note)}<br>${esc(a.lagna_time_diagnostic.note||'')}</p></div>`:''}
    <div class="note">${esc(a.warning||'')}</div>
  </div></div>`;
}
function resultHtml(result){ const current = result.dasha.current; let html = `<div class="summary-grid">${summaryCard('ලග්නය', result.lagna.rashi.name, `${Number(result.lagna.rashi.degree || 0).toFixed(2)}°`)}${summaryCard('චන්ද්‍ර රාශිය', result.moon_sign.name, result.birth_nakshatra.name + ' • පාදය ' + result.birth_nakshatra.pada)}${summaryCard('ගණන ආකාරය', result.mode === 'reference' ? 'මුල් කේන්දර අගයන්' : 'ගණනය කළ', result.mode === 'reference' ? 'අතින් දුන් මුල් කේන්දර අගයන්' : (result.person.timezone_source || ''))}${summaryCard('වත්මන් දශාව', current ? current.name : '—', current ? ((current.start || '') + (current.end ? ' සිට ' + current.end : '')) : '')}</div>`; html += `<div class="actions-row"><button class="outline-btn ${result.mode==='reference'?'ref-report-btn':'birth-report-btn'}">වාර්තාව මුද්‍රණය / පීඩීඑෆ්</button><button class="outline-btn top-btn">ඉහළට</button></div>`; html += `<div class="result-grid"><div>${squareChart(result.rashi_chart,'රාශි කේන්දරය', result.lagna?.rashi)}${planetsTable(result.planets)}</div><div>${squareChart(result.navamsa_chart,'නවාංශ කේන්දරය', result.lagna?.navamsa || result.lagna?.rashi)}${housesPanel(result.houses)}</div></div>`; html += auditPanel(result.calculation_audit); html += advancedPanel(result.advanced); html += `<div class="result-grid" style="margin-top:18px"><div>${readingPanel(result.reading)}</div><div>${dashaPanel(result.dasha)}<div class="note">${esc(result.disclaimer)}</div>${result.person.source_notes ? `<div class="panel" style="margin-top:14px"><h3>මුල් සටහන්</h3><div class="note" style="margin-top:0">${esc(result.person.source_notes).replace(/\n/g,'<br>')}</div></div>` : ''}</div></div>`; return html; }
function attachResultActions(container, result, mode){ container.querySelector('.top-btn').onclick = ()=>window.scrollTo({top:0,behavior:'smooth'}); const btn = container.querySelector(mode==='reference'?'.ref-report-btn':'.birth-report-btn'); if(btn) btn.onclick = ()=>openReportWindow(result); }
function renderBirth(result){ lastBirthResult = result; const container = $('#birthResults'); container.innerHTML = resultHtml(result); container.classList.remove('hidden'); attachResultActions(container, result, 'birth'); container.scrollIntoView({behavior:'smooth', block:'start'}); }
function renderReference(result){ lastReferenceResult = result; const container = $('#refResults'); container.innerHTML = resultHtml(result); container.classList.remove('hidden'); attachResultActions(container, result, 'reference'); container.scrollIntoView({behavior:'smooth', block:'start'}); }
$('#birthForm').addEventListener('submit', async (e)=>{ e.preventDefault(); $('#birthLoading').classList.remove('hidden'); $('#birthResults').classList.add('hidden'); try { renderBirth(await post('/api/calculate', mainPayload())); } catch(err){ $('#birthResults').innerHTML = `<div class="panel"><h3>දෝෂයක්</h3><div class="note">${esc(err.message)}</div></div>`; $('#birthResults').classList.remove('hidden'); } finally { $('#birthLoading').classList.add('hidden'); } });
$('#refForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  $('#refLoading').classList.remove('hidden');
  $('#refResults').classList.add('hidden');
  try {
    const pack = await post('/api/autofill_reference', {birth: referenceBirthPayload(), anchors: referenceAnchors()});
    renderReference(pack.analysis);
  } catch(err){
    $('#refResults').innerHTML = `<div class="panel"><h3>දෝෂයක්</h3><div class="note">${esc(err.message)}</div></div>`;
    $('#refResults').classList.remove('hidden');
  } finally {
    $('#refLoading').classList.add('hidden');
  }
});
$('#compareBtn').addEventListener('click', async ()=>{
  const target = $('#refResults');
  target.classList.remove('hidden');
  target.innerHTML = `<div class="panel"><h3>සැසඳීම සිදු කරමින්...</h3></div>`;
  try {
    const birth = referenceBirthPayload();
    const anchors = referenceAnchors();
    const pack = await post('/api/autofill_reference', {birth, anchors});
    const calc = pack.calculated;
    const ref = pack.analysis;
    const rows = [];
    const add = (item,a,b,hasAnchor=true)=>{ if(hasAnchor) rows.push({item,a,b,ok:String(a)===String(b)}); };
    add('ලග්නය', calc.lagna.rashi.name, ref.lagna.rashi.name, anchors.lagna_sign_index !== undefined);
    add('චන්ද්‍ර රාශිය', calc.moon_sign.name, ref.moon_sign.name, anchors.moon_sign_index !== undefined);
    add('ජන්ම නැකත', calc.birth_nakshatra.name, ref.birth_nakshatra.name, anchors.nakshatra_index !== undefined);
    add('නැකත් පාදය', calc.birth_nakshatra.pada, ref.birth_nakshatra.pada, anchors.nakshatra_pada !== undefined);
    add('වත්මන් මහා දශාව', calc.dasha.current ? calc.dasha.current.name : '—', ref.dasha.current ? ref.dasha.current.name : '—', !!anchors.current_mahadasha);
    if(!rows.length){
      target.innerHTML = `<div class="panel"><h3>සැසඳීමේ ප්‍රතිඵලය</h3><div class="note">මුල් කේන්දරයේ අගයක් දාලා නැති නිසා සැසඳීමට දත්ත නොමැත. ස්වයංක්‍රීය ගණනයෙන් ලැබෙන විග්‍රහය සෘජුව බලන්න පුළුවන්.</div></div>`;
      return;
    }
    const okCount = rows.filter(x=>x.ok).length;
    target.innerHTML = `<div class="panel"><div class="panel-head"><h3>මුල් කේන්දරය සහ ස්වයංක්‍රීය ගණනය සැසඳීම</h3><div class="micro">${okCount} / ${rows.length} ගැලපේ</div></div><div class="note">ගණනය කළ අගය පද්ධතියෙන් ලැබෙන අගයයි. මුල් අගය ලෙස ඔබ දුන් පරණ කේන්දර අගය පෙන්වයි.</div><div class="table-wrap"><table class="compare-table"><thead><tr><th>කරුණ</th><th>ගණනය කළ අගය</th><th>මුල් අගය</th><th>තත්ත්වය</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(r.item)}</td><td>${esc(r.a)}</td><td>${esc(r.b)}</td><td class="${r.ok?'status-good':'status-bad'}">${r.ok?'ගැලපේ':'නොගැලපේ'}</td></tr>`).join('')}</tbody></table></div></div>`;
    target.insertAdjacentHTML('afterbegin','<div class="compare-printbar"><button class="outline-btn" id="printCompareBtn">සැසඳීම මුද්‍රණය / පීඩීඑෆ්</button></div>');document.getElementById('printCompareBtn').onclick=()=>printableWindow('මුල් කේන්දරය සහ ගණනය සැසඳීම',target.innerHTML,'ගණිත සත්‍යාපන වාර්තාව');target.scrollIntoView({behavior:'smooth', block:'start'});
  } catch(err){ target.innerHTML = `<div class="panel"><h3>දෝෂයක්</h3><div class="note">${esc(err.message)}</div></div>`; }
});


function porondamRadarChart(d){
  const cats=(d.categories||[]).slice(0,8);
  if(cats.length<3) return '';
  const cx=210,cy=210,maxR=138,n=cats.length;
  const point=(i,r)=>{const a=(-Math.PI/2)+(Math.PI*2*i/n);return [cx+Math.cos(a)*r,cy+Math.sin(a)*r]};
  const poly=(scale)=>cats.map((_,i)=>point(i,maxR*scale).map(v=>v.toFixed(1)).join(',')).join(' ');
  const dataPts=cats.map((c,i)=>point(i,maxR*Math.max(0,Math.min(100,Number(c.percent||0)))/100));
  const dataPoly=dataPts.map(p=>p.map(v=>v.toFixed(1)).join(',')).join(' ');
  const axes=cats.map((_,i)=>{const p=point(i,maxR);return `<line class="radar-axis" x1="${cx}" y1="${cy}" x2="${p[0].toFixed(1)}" y2="${p[1].toFixed(1)}"/>`}).join('');
  const dots=dataPts.map(p=>`<circle class="radar-dot" cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="4.5"/>`).join('');
  const labels=cats.map((c,i)=>{const p=point(i,maxR+35);let y=p[1]; if(y<40)y=40;if(y>389)y=389;return `<text class="radar-label" x="${p[0].toFixed(1)}" y="${y.toFixed(1)}">${esc(c.name)}</text><text class="radar-value" x="${p[0].toFixed(1)}" y="${(y+14).toFixed(1)}">${Math.round(Number(c.percent||0))}%</text>`}).join('');
  const pct=Math.round(Number(d.score||0));
  return `<div class="porondam-glass-chart"><div class="porondam-chart-head"><h3>ගැලපුම් වෘත්තය</h3><span>අංශ අනුව ගැලපීම</span></div><div class="porondam-radar-wrap"><svg class="porondam-radar" viewBox="0 0 420 420" role="img" aria-label="පොරොන්දම් ගැලපුම් වෘත්තය"><defs><linearGradient id="radarFill" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6cb70" stop-opacity=".54"/><stop offset=".52" stop-color="#7f3250" stop-opacity=".48"/><stop offset="1" stop-color="#3ea7db" stop-opacity=".38"/></linearGradient><filter id="radarGlow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>${[1,.75,.5,.25].map(s=>`<polygon class="radar-grid" points="${poly(s)}"/>`).join('')}${axes}<polygon class="radar-area" points="${dataPoly}"/>${dots}${labels}<circle class="radar-score-ring" cx="${cx}" cy="${cy}" r="58"/><text class="radar-score" x="${cx}" y="${cy+7}">${pct}%</text><text class="radar-score-sub" x="${cx}" y="${cy+28}">සමස්ත ගැලපීම</text></svg></div></div>`;
}


function porondamFactorMeaning(name){
  const map={
    'දින / තාරා පොරොන්දම':'දෙදෙනාගේ නැකත් අතර සාම්ප්‍රදායික සුභ-අසුභ දුර සලකා දෛනික ජීවිතයේ සහයෝගය, සෞභාග්‍යය සහ එකිනෙකාට ලැබෙන සහාය පිළිබඳ ඉඟියක් ලබාදේ.',
    'ගණ පොරොන්දම':'දේව, මනුෂ්‍ය සහ රාක්ෂස ගණ වර්ග අනුව ස්වභාවය, ප්‍රතිචාර රටාව සහ එකිනෙකා සමඟ හැසිරෙන ආකාරය සසඳයි.',
    'මහේන්ද්‍ර පොරොන්දම':'පවුල් වර්ධනය, එකිනෙකාට ආරක්ෂාව සහ දිගුකාලීන සහයෝගය ගැන සාම්ප්‍රදායිකව සලකා බලන අංශයකි.',
    'ස්ත්‍රී දීර්ඝ පොරොන්දම':'ස්ත්‍රී පාර්ශවයේ නැකතෙන් පුරුෂ පාර්ශවයේ නැකතට ඇති දුර අනුව විවාහ ජීවිතයේ ස්ථාවරත්වය ගැන සලකා බලයි.',
    'යෝනි පොරොන්දම':'ශාරීරික ආකර්ෂණය, සමීපභාවය සහ ස්වභාවික රුචි අරුචිකම් අතර ගැලපීම සංකේතාත්මකව පරීක්ෂා කරයි.',
    'රාශි පොරොන්දම':'චන්ද්‍ර රාශි දෙකේ සම්බන්ධතාවය අනුව හැඟීම්, මනෝභාවය සහ දෛනික අවබෝධය සසඳයි.',
    'රාශි අධිපති මෛත්‍රී':'චන්ද්‍ර රාශි අධිපති ග්‍රහ දෙකේ මිත්‍රත්වය අනුව අදහස් හුවමාරුව සහ එකිනෙකාට සහය වීම සලකා බලයි.',
    'වශ්‍ය පොරොන්දම':'එකිනෙකා කෙරෙහි ඇති ආකර්ෂණය, අනුගත වීම සහ සබඳතාව පවත්වාගෙන යාමේ පහසුව ගැන ඉඟියක් ලබාදේ.',
    'රජ්ජු පොරොන්දම':'විවාහයේ දිගුකාලීන ස්ථාවරත්වය සම්බන්ධයෙන් හෙළ/දකුණු ඉන්දීය සම්ප්‍රදායේ විශේෂ අවධානයක් දෙන අංශයකි.',
    'වේධ පොරොන්දම':'නැකත් දෙක අතර විශේෂ විරෝධී සම්බන්ධතාවක් තිබේදැයි පරීක්ෂා කරන සාම්ප්‍රදායික අංශයකි.',
    'නාඩි පොරොන්දම':'ශරීර-ප්‍රකෘති සහ පවුල් වර්ධනය සම්බන්ධයෙන් සාම්ප්‍රදායිකව වැදගත් කරුණක් ලෙස සලකයි.',
    'වර්ණ පොරොන්දම':'මානසික පරිණතභාවය සහ සමාජ/චරිත ගුණ අතර ගැලපීම සංකේතාත්මකව සසඳයි.',
    'නැකත් අධිපති මෛත්‍රී':'ජන්ම නැකත් පාලක ග්‍රහයන්ගේ සම්බන්ධතාවය අනුව අදහස් හා හැසිරීම් ගැලපීම බලයි.',
    'චන්ද්‍ර දුර ගැලපීම':'චන්ද්‍ර රාශි සහ නැකත් චක්‍රයේ දුර අනුව මානසික සහ චිත්තවේගීය රිද්මය සසඳයි.',
    'ලග්න ගැලපීම':'දෙදෙනාගේ ජීවන රටාව, දෛනික හැසිරීම සහ පොදු ජීවිත දිශාව ලග්න දෙකෙන් සසඳයි.',
    'සත්වන භාව අධිපති ගැලපීම':'විවාහ භාවය පාලනය කරන ග්‍රහයන් දෙක සසඳා විවාහ ජීවිතයේ ස්ථාවරත්වයට අදාළ ඉඟි ලබාදේ.',
    'ශුක්‍ර ගැලපීම':'ආදරය, ආකර්ෂණය, සතුට සහ සම්බන්ධතා රසය සම්බන්ධ ශුක්‍ර පිහිටීම් සසඳයි.',
    'ගුරු ගැලපීම':'වටිනාකම්, පවුල් වර්ධනය, උපදේශනමය සහය සහ දීර්ඝකාලීන දියුණුව සම්බන්ධ ගුරු පිහිටීම් සසඳයි.',
    'කුජ දෝෂ සමානතාව':'කුජ බලපෑම ලග්නය, චන්ද්‍රය සහ ශුක්‍රය අනුව දෙදෙනාට සමානදැයි පරීක්ෂා කරයි. සමාන බලපෑම් ඇති විට සාම්ප්‍රදායිකව එය සමතුලිත බවක් ලෙස සලකයි.',
    'දශා කාල ගැලපීම':'දැනට ක්‍රියාත්මක මහා දශා දෙක අතර සම්බන්ධතාවය බලමින් එකම කාලයේ දෙදෙනා මුහුණ දෙන ජීවන පීඩන සහ අවස්ථා සසඳයි.'
  };
  return map[name]||'මෙම අංශය සම්පූර්ණ කේන්දර ගැලපීමේ එක් සාම්ප්‍රදායික කොටසක් ලෙස සලකා බලයි.';
}
function porondamExplanation(d){
  const pct=Math.round(Number(d.score||0));
  const factors=Array.isArray(d.factors)?d.factors:[];
  const strong=factors.filter(f=>Number(f.score)>=.75).sort((a,b)=>(b.weight||0)-(a.weight||0)).slice(0,5);
  const weak=factors.filter(f=>Number(f.score)<.4).sort((a,b)=>(b.weight||0)-(a.weight||0)).slice(0,5);
  const medium=factors.filter(f=>Number(f.score)>=.4&&Number(f.score)<.75).slice(0,4);
  const critical=(d.critical_flags||[]);
  let meaning='මෙම ප්‍රතිශතය නැකත්, රාශි, ලග්න, විවාහ භාව, ග්‍රහ සම්බන්ධතා, කුජ දෝෂ සහ දශා කාලය එකට සලකා ලබාගත් සාරාංශ අගයකි.';
  if(pct>=80) meaning+=' සාම්ප්‍රදායික ගණනය අනුව බොහෝ ප්‍රධාන අංශ එකිනෙකාට සහය වන බව පෙන්වයි.';
  else if(pct>=65) meaning+=' ප්‍රධාන අංශ බොහොමයක් හොඳ වුවත් මධ්‍යම හෝ අවධානය යොමු කළ යුතු කරුණු කිහිපයක් තිබිය හැක.';
  else if(pct>=50) meaning+=' හොඳ සහ අභියෝගාත්මක අංශ දෙකම මිශ්‍රව පෙනෙන නිසා සම්පූර්ණ කේන්දර දෙක ගැඹුරින් බලන එක වැදගත්ය.';
  else meaning+=' අත්‍යවශ්‍ය හෝ බර වැඩි අංශ කිහිපයක අඩු ගැලපීමක් තිබිය හැකි නිසා ප්‍රතිශතය පමණක් මත තීරණ නොගත යුතුය.';
  const list=(arr,empty)=>arr.length?`<ul>${arr.map(f=>`<li><b>${esc(f.name)}</b> — ${esc(f.note||'')}<br><span class="factor-meaning">${esc(porondamFactorMeaning(f.name))}</span></li>`).join('')}</ul>`:`<p>${empty}</p>`;
  return `<div class="porondam-meaning-panel"><h3>මෙම ගැලපීමෙන් අදහස් කරන්නේ මොකක්ද?</h3><p>${esc(meaning)}</p><div class="porondam-band"><div><b>80% – 100%</b>ඉතා හොඳ ගැලපීම</div><div><b>65% – 79%</b>හොඳ ගැලපීම</div><div><b>50% – 64%</b>මධ්‍යම ගැලපීම</div><div><b>50% ට අඩු</b>ගැඹුරු විග්‍රහයක් අවශ්‍යයි</div></div><div class="porondam-explain-grid"><div class="porondam-explain-card good"><h4>හොඳින් ගැලපෙන ප්‍රධාන කරුණු</h4>${list(strong,'විශේෂයෙන් ඉහළ ලකුණු ලැබූ අංශ නොපෙනේ.')}</div><div class="porondam-explain-card warn"><h4>අවධානය යොමු කළ යුතු කරුණු</h4>${list(weak.length?weak:medium,'ප්‍රධාන අඩු ගැලපීම් හඳුනාගෙන නොමැත.')}</div><div class="porondam-explain-card core"><h4>අවසන් තේරුම</h4><p><b>${esc(d.verdict||'')}</b></p><p>${critical.length?`විශේෂ අවධානය: ${esc(critical.join(', '))}. මේවා බර වැඩි සාම්ප්‍රදායික කරුණු නිසා සම්පූර්ණ කේන්දර දෙක, දශා සහ විවාහ භාවය එක්ක නැවත සලකා බලන්න.`:'අත්‍යවශ්‍ය ලෙස සලකන ප්‍රධාන විරෝධී ලකුණු දැනට හඳුනාගෙන නැත. එහෙත් විවාහ තීරණයකදී සන්නිවේදනය, පවුල් පසුබිම, අරමුණු සහ සැබෑ ජීවිත ගැලපීමත් එකසේ වැදගත්ය.'}</p></div></div></div>`;
}

function renderMatch(d){
  const pct = Math.round(Number(d.score||0));
  const cls = (f)=>f.score >= .75 ? 'good' : (f.score >= .4 ? 'mid' : 'bad');
  let html = `<div class="porondam-visual-grid">${porondamRadarChart(d)}<div class="porondam-summary-glass"><div class="porondam-score-big"><div class="porondam-score-orb" style="--pct:${pct}"><strong>${pct}%</strong></div><div class="porondam-score-copy"><h3>${esc(d.verdict||'පොරොන්දම් සාරාංශය')}</h3><p>නැකත්, රාශි, අත්‍යවශ්‍ය කරුණු, සම්පූර්ණ කේන්දර සම්බන්ධතා සහ කාල ගැලපීම එකට සලකා ලබාගත් සමස්ත ප්‍රතිඵලය.</p></div></div><div class="porondam-persons"><div class="porondam-person"><b>ස්ත්‍රී පාර්ශවය — ${esc(d.bride_summary.name)}</b><span>${esc(d.bride_summary.nakshatra.name)} • ${esc(d.bride_summary.moon_sign.name)} • ලග්න ${esc(d.bride_summary.lagna?.name||'—')}</span></div><div class="porondam-person"><b>පුරුෂ පාර්ශවය — ${esc(d.groom_summary.name)}</b><span>${esc(d.groom_summary.nakshatra.name)} • ${esc(d.groom_summary.moon_sign.name)} • ලග්න ${esc(d.groom_summary.lagna?.name||'—')}</span></div></div><div class="porondam-category-chips">${(d.categories||[]).map(c=>`<div class="porondam-category-chip"><b>${Math.round(Number(c.percent||0))}%</b><span>${esc(c.name)}</span></div>`).join('')}</div></div></div>`;
  html += `<div class="panel" style="margin-top:18px"><div class="panel-head"><h3>ගැලපුම් අංශ</h3><div class="micro">විස්තීර්ණ අංශ 20</div></div><div class="category-grid">${(d.categories||[]).map(c=>`<div class="category-card"><span>${esc(c.name)}</span><b>${c.percent}%</b></div>`).join('')}</div></div>`;
  html += porondamExplanation(d);
  html += `<div class="panel" style="margin-top:18px"><div class="panel-head"><h3>පොරොන්දම් හා සම්පූර්ණ කේන්දර ගැලපීම් 20</h3><div class="micro">බර අනුව ලකුණු</div></div><div class="match-grid">${d.factors.map(f=>`<div class="match-item"><div class="match-top"><b>${esc(f.name)}</b><span class="grade ${cls(f)}">${esc(f.grade)}</span></div><div>${esc(f.note)}</div><span class="factor-meaning">${esc(porondamFactorMeaning(f.name))}</span><small>${esc(f.category||'')} • බර ${esc(f.weight)}</small></div>`).join('')}</div><div class="note">${esc(d.note)}${(d.critical_flags||[]).length ? '<br><br><b>විශේෂ අවධානය:</b> ' + esc((d.critical_flags||[]).join(', ')) : ''}</div></div>`;
  if(d.kuja){ html += `<div class="panel" style="margin-top:18px"><div class="panel-head"><h3>කුජ දෝෂ සමානතාව</h3><div class="micro">ලග්න • චන්ද්‍ර • ශුක්‍ර</div></div><div class="couple-grid"><div class="mini-card"><h3>ස්ත්‍රී පාර්ශවය ${d.kuja.bride}/3</h3>${(d.kuja.bride_refs||[]).map(x=>`<div class="flag-card">${esc(x[0])}: ${esc(x[1])} වන භාවය ${x[2]?'• සැලකිල්ලට':''}</div>`).join('')}</div><div class="mini-card"><h3>පුරුෂ පාර්ශවය ${d.kuja.groom}/3</h3>${(d.kuja.groom_refs||[]).map(x=>`<div class="flag-card">${esc(x[0])}: ${esc(x[1])} වන භාවය ${x[2]?'• සැලකිල්ලට':''}</div>`).join('')}</div></div></div>`; }
  $('#matchResults').innerHTML = html; $('#matchResults').classList.remove('hidden'); $('#matchResults').scrollIntoView({behavior:'smooth', block:'start'});
}
$('#matchForm').addEventListener('submit', async (e)=>{ e.preventDefault(); $('#matchLoading').classList.remove('hidden'); $('#matchResults').classList.add('hidden'); try { renderMatch(await post('/api/porondam', {groom:payload('groom'), bride:payload('bride')})); } catch(err){ $('#matchResults').innerHTML = `<div class="panel"><h3>දෝෂයක්</h3><div class="note">${esc(err.message)}</div></div>`; $('#matchResults').classList.remove('hidden'); } finally { $('#matchLoading').classList.add('hidden'); } });

function reportChart(cells, title, lagnaInfo){ const corners={0:'r-corner-tl',3:'r-corner-tr',9:'r-corner-bl',12:'r-corner-br'}; const box = (cell,corner='')=>`<div class="r-box ${corner}"><div class="r-sign">${esc(cell.sign)} <span>${cell.sign_index+1}</span></div><div class="r-occ">${cell.planets.length ? cell.planets.map(x=>esc(shortPlanetLabel(x))).join('<br>') : ''}</div></div>`; const li=lagnaInfo||{}; const idx=Number(li.index??0); const nm=li.name||SIGNS[idx]||'—'; const deg=Number(li.degree); let html = `<div class="report-chart-block"><div class="report-chart-head"><h4>${esc(title)}</h4><small>ශ්‍රී ලංකා සාම්ප්‍රදායික ආකෘතිය</small></div><div class="report-chart sri-report-chart">`; chartOrder.forEach((item,pos)=>{ if(item === 'center') html += `<div class="r-center"><img class="r-zodiac-img" src="/static/zodiac/${idx}.svg" alt="${esc(nm)}"><span class="r-lagna-label">ලග්නය</span><strong>${esc(nm)}</strong>${Number.isFinite(deg)?`<b>${deg.toFixed(2)}°</b>`:''}<small>${esc(title)}</small></div>`; else html += box(cells[item],corners[pos]||''); }); html += `</div><div class="report-chart-legend">ග්‍රහ නාම කෙටි අක්ෂරයෙන් • ℞ = වක්‍ර ගමන</div></div>`; return html; }
function openReportWindow(data){
  const cfg=getSettings();
  const vcode=reportCode(data.mode==='reference'?'HV':'HJ');
  const win = window.open('', '_blank');
  if(!win) return alert('නව කවුළුව විවෘත කිරීමට අවසර දෙන්න.');
  const current = data.dasha.current;
  const planets = Object.values(data.planets);
  const sections = data.reading.sections || [];
  const sectionCards = sections.map((s,i)=>`<div class="analysis-card"><div class="analysis-num">${String(i+1).padStart(2,'0')}</div><div><h3>${esc(s.title)}</h3><p>${esc(s.text)}</p></div></div>`).join('');
  const toc = sections.map((s,i)=>`<div class="toc-row"><span>${String(i+1).padStart(2,'0')}</span><b>${esc(s.title)}</b></div>`).join('');
  const dashaRows = (data.dasha.periods && data.dasha.periods.length ? data.dasha.periods : (data.dasha.current ? [data.dasha.current] : []));
  const sourceNotes = data.person.source_notes ? `<section class="book-page"><div class="page-title">මුල් කේන්දර සටහන්</div><div class="note-paper">${esc(data.person.source_notes).replace(/\n/g,'<br>')}</div><div class="page-foot">${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')} • මුල් සටහන්</div></section>` : '';
  const styles = `<style>
    :root{--ink:#24181b;--wine:#742638;--wine2:#42161f;--gold:#c49b51;--cream:#fbf6ee;--line:#e7d8c6;--muted:#796b6f}
    *{box-sizing:border-box} @page{size:A4;margin:12mm 13mm 14mm}
    body{margin:0;background:#ece6dc;color:var(--ink);font-family:"Noto Sans Sinhala","Iskoola Pota","Nirmala UI",sans-serif}
    .printbar{position:sticky;top:0;z-index:20;background:#fff;padding:10px 18px;border-bottom:1px solid #ddd;display:flex;justify-content:flex-end;gap:8px}
    .printbar button{border:none;background:linear-gradient(135deg,var(--wine),#a13c51);color:#fff;padding:11px 18px;border-radius:12px;font-weight:900;cursor:pointer}.printbar .secondary{background:#fff;color:var(--wine);border:1px solid #d9c9b4}
    .book{max-width:210mm;margin:0 auto;background:#fff;box-shadow:0 20px 60px rgba(0,0,0,.12)}
    .book-page{min-height:270mm;padding:12mm 10mm 12mm;page-break-after:always;position:relative;background:linear-gradient(180deg,#fff,#fffdf9)}
    .book-page:last-child{page-break-after:auto}.page-foot{position:absolute;left:10mm;right:10mm;bottom:5mm;padding-top:2mm;border-top:1px solid var(--line);font-size:9px;color:#8e8084;display:flex;justify-content:space-between}
    .cover{min-height:270mm;padding:20mm 18mm;display:flex;flex-direction:column;justify-content:center;background:radial-gradient(circle at 85% 18%,rgba(196,155,81,.14),transparent 23%),linear-gradient(180deg,#fffdf8,#f8efe3);border:1px solid #eadcc9;position:relative;overflow:hidden}
    .cover:before,.cover:after{content:"";position:absolute;border:1px solid rgba(196,155,81,.35);border-radius:50%;right:-22mm;top:18mm}.cover:before{width:74mm;height:74mm}.cover:after{width:50mm;height:50mm;right:-10mm;top:30mm}
    .seal{width:24mm;height:24mm;border-radius:50%;display:grid;place-items:center;background:linear-gradient(135deg,var(--wine2),var(--wine));color:#f1d296;font-size:20px;margin-bottom:9mm;box-shadow:0 8px 20px rgba(71,25,34,.18)}
    .cover-kicker{font-size:11px;text-transform:uppercase;letter-spacing:.16em;color:var(--wine);font-weight:900}.cover-title{font-family:Georgia,"Nirmala UI",serif;font-size:34px;line-height:1.15;margin:5mm 0 4mm;color:#271a1d}.cover-sub{font-size:15px;color:#765f64;line-height:1.8;max-width:130mm}.cover-name{font-size:22px;font-weight:900;color:var(--wine);margin-top:12mm}.cover-meta{margin-top:5mm;display:grid;grid-template-columns:1fr 1fr;gap:2.5mm 6mm;font-size:11px;color:#58494d}.cover-meta div{padding:3mm 0;border-bottom:1px solid #eadbc8}.cover-meta b{color:#2d2023}.cover-note{margin-top:12mm;padding:4mm 5mm;border-left:3px solid var(--gold);background:#fff9ef;color:#6d5d61;font-size:10px;line-height:1.7;max-width:145mm}
    .page-kicker{font-size:10px;text-transform:uppercase;letter-spacing:.13em;color:var(--gold);font-weight:900}.page-title{font-family:Georgia,"Nirmala UI",serif;font-size:25px;color:var(--wine);margin:2mm 0 6mm}.section-intro{color:var(--muted);font-size:11px;line-height:1.7;margin-bottom:6mm}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm}.summary-box{border:1px solid var(--line);background:#fffaf3;border-radius:12px;padding:4mm;min-height:25mm}.summary-box small{display:block;color:#88777b;font-size:9px;font-weight:900;text-transform:uppercase;letter-spacing:.04em}.summary-box strong{display:block;color:var(--wine);font-size:16px;margin-top:2mm}.summary-box span{display:block;color:#74686b;font-size:9px;line-height:1.45;margin-top:1mm}.executive{margin-top:6mm;border:1px solid var(--line);border-radius:14px;padding:5mm;background:linear-gradient(180deg,#fffdf9,#fff8ef)}.executive h3{margin:0 0 3mm;color:var(--wine);font-size:15px}.executive li{margin-bottom:2mm;line-height:1.65;font-size:11px}.toc{display:grid;grid-template-columns:1fr 1fr;gap:3mm 7mm}.toc-row{display:grid;grid-template-columns:10mm 1fr;align-items:center;border-bottom:1px solid #eee2d4;padding:3mm 0}.toc-row span{color:var(--gold);font-weight:900}.toc-row b{font-size:10.5px;color:#4e4144}
    .two{display:grid;grid-template-columns:1fr 1fr;gap:6mm}.report-chart-head{display:flex;align-items:end;justify-content:space-between;margin-bottom:2.5mm}.report-chart-head h4{margin:0;color:var(--wine);font-size:13px}.report-chart-head small{font-size:7.5px;color:#8c7a70;font-weight:700}.report-chart{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1.5px solid #9a7443;background:#f7f1e7;aspect-ratio:1/1}.r-box,.r-center{position:relative;border:0;border-radius:0;padding:2mm;min-height:0;background:#fffdf8;box-shadow:inset 0 0 0 .55px #26313a;overflow:hidden}.r-center{grid-column:2 / span 2;grid-row:2 / span 2;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;background:#fffaf2}.r-zodiac-img{width:18mm;height:18mm;object-fit:contain;display:block;margin:0 auto 1mm}.r-lagna-label{font-size:7.5px;font-weight:900;color:#7b684e;letter-spacing:.04em}.r-center strong{font-size:13px;line-height:1.1;color:var(--wine)}.r-center b{font-size:8px;color:#5b4c48;margin-top:.6mm}.r-center small{display:block;color:#8b7d7f;font-size:7px;margin-top:.8mm}.r-sign{position:relative;z-index:2;font-size:8.5px;font-weight:900;color:var(--wine)}.r-sign span{float:right;color:#b29360}.r-occ{position:relative;z-index:2;margin-top:1.5mm;font-size:9px;font-weight:800;line-height:1.35;text-align:center;color:#172536}.r-corner-tl:after,.r-corner-tr:after,.r-corner-bl:after,.r-corner-br:after{content:"";position:absolute;left:50%;top:50%;width:142%;height:.55px;background:#26313a;transform-origin:center;z-index:1}.r-corner-tl:after,.r-corner-br:after{transform:translate(-50%,-50%) rotate(45deg)}.r-corner-tr:after,.r-corner-bl:after{transform:translate(-50%,-50%) rotate(-45deg)}.report-chart-legend{text-align:center;font-size:7px;color:#8b7d7f;margin-top:1.5mm}.houses-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin-top:6mm}.house{border:1px solid var(--line);border-radius:10px;padding:3mm;background:#fffdf9}.house b{font-size:10px;color:var(--wine)}.house small{display:block;font-size:8.5px;color:#817477;margin:1mm 0}.pill{display:inline-block;padding:1mm 2mm;border-radius:999px;background:#f4eadb;font-size:8px;margin:1px}
    table{width:100%;border-collapse:collapse;font-size:9px}th,td{padding:2.4mm 1.7mm;border-bottom:1px solid #ede1d3;text-align:left;vertical-align:top}th{background:#fbf3e9;color:#6e5c60;font-size:8px;text-transform:uppercase;letter-spacing:.03em}
    .analysis-grid{display:grid;grid-template-columns:1fr 1fr;gap:4mm}.analysis-card{border:1px solid var(--line);border-radius:13px;padding:4mm;background:linear-gradient(180deg,#fff,#fffaf4);break-inside:avoid;display:grid;grid-template-columns:9mm 1fr;gap:3mm}.analysis-num{width:8mm;height:8mm;border-radius:50%;display:grid;place-items:center;background:#7a2638;color:#fff;font-size:8px;font-weight:900}.analysis-card h3{font-size:12px;color:var(--wine);margin:0 0 2mm}.analysis-card p{font-size:9.4px;line-height:1.65;margin:0;color:#493d40}.note-paper{border:1px solid var(--line);border-radius:12px;padding:6mm;background:repeating-linear-gradient(#fffdf9,#fffdf9 7mm,#f0e7da 7.2mm);font-size:10px;line-height:1.8;min-height:110mm}.disclaimer{margin-top:6mm;padding:4mm;border-radius:10px;background:#fff7e9;border:1px solid #ead8b7;font-size:9px;line-height:1.65;color:#75676a}
    .end-card{text-align:center;padding:20mm 10mm}.end-symbol{font-size:40px;color:var(--wine)}.end-title{font-family:Georgia,"Nirmala UI",serif;color:var(--wine);font-size:22px;margin:4mm 0}.end-text{font-size:10px;color:#76696c;line-height:1.8;max-width:120mm;margin:auto}
    @media print{body{background:#fff}.printbar{display:none}.book{box-shadow:none;max-width:none}.book-page,.cover{min-height:auto}.book-page{padding:0}.page-foot{bottom:-7mm}.analysis-card{break-inside:avoid}.cover{border:none}}
  </style>`;
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>${esc(data.person.name || 'කේන්දරය')} - කේන්දර වාර්තාව</title>${styles}</head><body class="${esc(cfg.template||'classic')}">${trialWatermarkHtml()}
  <div class="printbar"><button class="secondary" onclick="window.close()">වසන්න</button><button onclick="window.print()">පීඩීඑෆ් ලෙස සුරකින්න / මුද්‍රණය</button></div>
  <main class="book">
    <section class="cover">
      ${cfg.logo?`<img src="${cfg.logo}" style="max-height:22mm;max-width:45mm;object-fit:contain;margin-bottom:4mm">`:'<div class="seal">ॐ</div>'}<div class="cover-kicker">${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}${cfg.astrologer?` • ජ්‍යෝතිෂ්‍යවේදී: ${esc(cfg.astrologer)}`:''}</div>
      <div class="cover-title">${data.mode==='reference'?'පවතින කේන්දර සම්පූර්ණ විග්‍රහය':'ජන්ම කේන්දර සම්පූර්ණ විග්‍රහය'}</div>
      <div class="cover-sub">රාශි කේන්දරය, නවාංශය, භාව 12, ග්‍රහ පිහිටීම්, දශා කාල, ජීවිත අංශ 22ක විස්තරාත්මක සාම්ප්‍රදායික විග්‍රහය සහ ප්‍රායෝගික සටහන්.</div>
      <div class="cover-name">${esc(data.person.name || 'නම සටහන් කර නැත')}</div>
      <div class="cover-meta"><div><b>උපන් දිනය</b><br>${esc(data.person.birth_date || '-')}</div><div><b>උපන් වෙලාව</b><br>${esc(data.person.birth_time || '-')}</div><div><b>උපන් ස්ථානය</b><br>${esc(data.person.birth_place || '-')}</div><div><b>වාර්තා ආකාරය</b><br>${data.mode==='reference'?'මුල් කේන්දර අගයන් සමඟ':'ගණනය කළ කේන්දරය'}</div><div><b>ලග්නය</b><br>${esc(data.lagna.rashi.name)}</div><div><b>ජන්ම නැකත</b><br>${esc(data.birth_nakshatra.name)} - පාදය ${data.birth_nakshatra.pada}</div></div>
      <div class="cover-note">මෙම වාර්තාව සාම්ප්‍රදායික ජ්‍යෝතිෂ්‍ය විග්‍රහයක් ලෙස සකස් කර ඇත. සෞඛ්‍ය, මුදල්, නීතිමය හෝ වෙනත් වැදගත් තීරණ සඳහා අදාළ වෘත්තීය උපදෙස් වෙනම ලබාගන්න.</div>${(cfg.phone||cfg.address||cfg.email||cfg.creator)?`<div class="cover-note"><b>${esc(cfg.institute||'')}</b>${cfg.astrologer?`<br>ජ්‍යෝතිෂ්‍යවේදී: ${esc(cfg.astrologer)}`:''}${cfg.phone?`<br>දුරකථන: ${esc(cfg.phone)}`:''}${cfg.address?`<br>ලිපිනය: ${esc(cfg.address)}`:''}${cfg.email?`<br>විද්‍යුත් තැපෑල: ${esc(cfg.email)}`:''}${cfg.creator?`<br>පද්ධති නිර්මාණය: ${esc(cfg.creator)}`:''}</div>`:''}
    </section>

    <section class="book-page"><div class="page-kicker">01 • සාරාංශය</div><div class="page-title">මූලික සාරාංශය</div><div class="summary-grid"><div class="summary-box"><small>ලග්නය</small><strong>${esc(data.lagna.rashi.name)}</strong><span>${Number(data.lagna.rashi.degree || 0).toFixed(2)}°</span></div><div class="summary-box"><small>චන්ද්‍ර රාශිය</small><strong>${esc(data.moon_sign.name)}</strong><span>${esc(data.birth_nakshatra.name || '')}</span></div><div class="summary-box"><small>ජන්ම නැකත</small><strong>${esc(data.birth_nakshatra.name)}</strong><span>පාදය ${data.birth_nakshatra.pada}</span></div><div class="summary-box"><small>වත්මන් දශාව</small><strong>${esc(current ? current.name : '-')}</strong><span>${current ? esc((current.start||'') + ((current.end||'') ? ' - ' + current.end : '')) : ''}</span></div></div><div class="executive"><h3>ප්‍රධාන කියවීම</h3><ul>${data.reading.summary.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div><div class="page-title" style="font-size:18px;margin-top:8mm">වාර්තාවේ අන්තර්ගතය</div><div class="toc">${toc}</div><div class="page-foot"><span>${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</span><span>පුද්ගලික කේන්දර පොත</span></div></section>

    <section class="book-page"><div class="page-kicker">02 • කේන්දර කොටු</div><div class="page-title">කේන්දර කොටු සහ භාව සාරාංශය</div><div class="two">${reportChart(data.rashi_chart,'රාශි කේන්දරය',data.lagna?.rashi)}${reportChart(data.navamsa_chart,'නවාංශ කේන්දරය',data.lagna?.navamsa||data.lagna?.rashi)}</div><div class="houses-grid">${data.houses.map(h=>`<div class="house"><b>${h.house} වන භාවය - ${esc(h.rashi)}</b><small>අධිපති ${esc(h.lord)}</small>${h.planets.length ? h.planets.map(p=>`<span class="pill">${esc(p)}</span>`).join('') : '<span class="pill">ග්‍රහ නොමැත</span>'}</div>`).join('')}</div><div class="page-foot"><span>${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</span><span>කේන්දර සහ භාව</span></div></section>

    <section class="book-page"><div class="page-kicker">03 • ග්‍රහ දත්ත</div><div class="page-title">ග්‍රහ පිහිටීම්</div><div class="section-intro">ග්‍රහයා සිටින රාශිය, අංශක, භාවය, නැකත සහ නවාංශය මේ වගුවේ සාරාංශ කර ඇත.</div><table><thead><tr><th>ග්‍රහයා</th><th>රාශිය</th><th>අංශක</th><th>භාවය</th><th>නැකත</th><th>පාදය</th><th>නවාංශය</th></tr></thead><tbody>${planets.map(x=>`<tr><td><b>${esc(x.name)}</b>${x.retrograde ? ' • වක්‍ර' : ''}</td><td>${esc(x.rashi.name)}</td><td>${Number(x.rashi.degree || 0).toFixed(2)}°</td><td>${x.house || '—'}</td><td>${esc(x.nakshatra?.name || '—')}</td><td>${esc(x.nakshatra?.pada || '—')}</td><td>${esc(x.navamsa?.name || '—')}</td></tr>`).join('')}</tbody></table><div class="page-title" style="font-size:18px;margin-top:8mm">දශා කාල සටහන</div><table><thead><tr><th>දශාව</th><th>ආරම්භය</th><th>අවසානය</th><th>අවුරුදු</th></tr></thead><tbody>${dashaRows.map(p=>`<tr><td>${esc(p.name || '')}</td><td>${esc(p.start || '')}</td><td>${esc(p.end || '')}</td><td>${esc(p.years || '')}</td></tr>`).join('')}</tbody></table><div class="page-foot"><span>${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</span><span>ග්‍රහ සහ දශා</span></div></section>

    <section class="book-page"><div class="page-kicker">04 • විස්තරාත්මක විග්‍රහය</div><div class="page-title">සම්පූර්ණ ජීවිත විග්‍රහය - 1</div><div class="analysis-grid">${sections.slice(0,7).map((s,i)=>`<div class="analysis-card"><div class="analysis-num">${String(i+1).padStart(2,'0')}</div><div><h3>${esc(s.title)}</h3><p>${esc(s.text)}</p></div></div>`).join('')}</div><div class="page-foot"><span>${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</span><span>විග්‍රහය - 1</span></div></section>

    <section class="book-page"><div class="page-kicker">05 • විස්තරාත්මක විග්‍රහය</div><div class="page-title">සම්පූර්ණ ජීවිත විග්‍රහය - 2</div><div class="analysis-grid">${sections.slice(7,14).map((s,i)=>`<div class="analysis-card"><div class="analysis-num">${String(i+8).padStart(2,'0')}</div><div><h3>${esc(s.title)}</h3><p>${esc(s.text)}</p></div></div>`).join('')}</div><div class="page-foot"><span>${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</span><span>විග්‍රහය - 2</span></div></section>

    <section class="book-page"><div class="page-kicker">06 • දශා, ග්‍රහ බල සහ පිළියම්</div><div class="page-title">සම්පූර්ණ ජීවිත විග්‍රහය - 3</div><div class="analysis-grid">${sections.slice(14).map((s,i)=>`<div class="analysis-card"><div class="analysis-num">${String(i+15).padStart(2,'0')}</div><div><h3>${esc(s.title)}</h3><p>${esc(s.text)}</p></div></div>`).join('')}</div><div class="disclaimer">${esc(data.disclaimer)}</div><div class="page-foot"><span>${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</span><span>විග්‍රහය - 3</span></div></section>

    ${sourceNotes}

    <section class="book-page"><div class="end-card"><div class="end-symbol">ॐ</div><div class="end-title">වාර්තාව අවසන්</div>${cfg.signature?`<img src="${cfg.signature}" style="max-height:24mm;max-width:55mm;object-fit:contain;margin:6mm auto;display:block">`:''}${cfg.seal?`<img src="${cfg.seal}" style="max-height:22mm;max-width:50mm;object-fit:contain;margin:4mm auto;display:block">`:''}${reportVerificationHtml(vcode)}<div class="end-text">මෙම වාර්තාවේ <b>පීඩීඑෆ් ලෙස සුරකින්න / මුද්‍රණය</b> බොත්තම භාවිතා කර A4 පීඩීඑෆ් ගොනුවක් ලෙස සුරකින්න හෝ මුද්‍රණය කරන්න පුළුවන්. මුද්‍රණ සැකසුම්වල පසුබිම් රූප පෙන්වීම සක්‍රීය කළොත් අලංකරණය සම්පූර්ණයෙන් පෙනේ.</div></div><div class="page-foot"><span>${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</span><span>සකස් කළ දිනය: ${esc(data.generated_at || '')}</span>${cfg.footer?`<div class="disclaimer">${esc(cfg.footer)}</div>`:''}</div></section>
  </main></body></html>`;
  win.document.open(); win.document.write(html); win.document.close();
}


// පද්ධති සැකසුම්
(function(){
 const btn=document.getElementById('settingsBtn'), modal=document.getElementById('settingsModal'); if(!btn||!modal)return;
 const ids={institute:'setInstitute',astrologer:'setAstrologer',phone:'setPhone',address:'setAddress',email:'setEmail',creator:'setCreator',footer:'setFooter',template:'setTemplate'};
 function fill(){const c=getSettings();Object.entries(ids).forEach(([k,id])=>{const e=document.getElementById(id);if(e)e.value=c[k]||'';});}
 btn.onclick=()=>{fill();modal.classList.remove('hidden')}; document.getElementById('settingsClose').onclick=()=>modal.classList.add('hidden');
 document.getElementById('settingsSave').onclick=async()=>{const prev=getSettings();const c={...prev};Object.entries(ids).forEach(([k,id])=>{const el=document.getElementById(id);c[k]=(el.value||'').trim?el.value.trim():el.value;});const readFile=(id)=>new Promise(resolve=>{const f=document.getElementById(id)?.files?.[0];if(!f)return resolve(null);const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=()=>resolve(null);r.readAsDataURL(f);});const logo=await readFile('setLogo'),sig=await readFile('setSignature'),seal=await readFile('setSeal');if(logo)c.logo=logo;if(sig)c.signature=sig;if(seal)c.seal=seal;localStorage.setItem('jyotishya_settings',JSON.stringify(c));dbMirrorSet('jyotishya_settings',c);applySettings();modal.classList.add('hidden');};
 document.getElementById('settingsReset').onclick=()=>{localStorage.removeItem('jyotishya_settings');dbMirrorDelete('jyotishya_settings');fill();applySettings();};
 modal.addEventListener('click',e=>{if(e.target===modal)modal.classList.add('hidden')}); applySettings();
})();

function enableEditing(container){const items=[...container.querySelectorAll('.reading-card p,.reading-card li,.note')];const active=!container.classList.contains('edit-active');container.classList.toggle('edit-active',active);items.forEach(x=>x.contentEditable=active?'true':'false');return active;}
function saveEdits(container,result){const lis=[...container.querySelectorAll('.reading-summary li')];if(lis.length)result.reading.summary=lis.map(x=>x.innerText.trim());const cards=[...container.querySelectorAll('.detailed-reading-card')];cards.forEach((c,i)=>{const p=c.querySelector('p');if(p&&result.reading.sections[i])result.reading.sections[i].text=p.innerText.trim();});container.classList.remove('edit-active');[...container.querySelectorAll('[contenteditable]')].forEach(x=>x.contentEditable='false');}
const _attachResultActions=attachResultActions;attachResultActions=function(container,result,mode){_attachResultActions(container,result,mode);const row=container.querySelector('.actions-row');if(row){const e=document.createElement('button');e.className='outline-btn';e.textContent='විග්‍රහය සංස්කරණය';let editing=false;e.onclick=()=>{if(!editing){editing=enableEditing(container);e.textContent='සංස්කරණය සුරකින්න';}else{saveEdits(container,result);editing=false;e.textContent='විග්‍රහය සංස්කරණය';}};row.insertBefore(e,row.firstChild);}};
let lastMatchResult=null;const _renderMatch=renderMatch;renderMatch=function(d){lastMatchResult=d;_renderMatch(d);const r=document.getElementById('matchResults');const bar=document.createElement('div');bar.className='porondam-actions';bar.innerHTML='<button class="outline-btn" id="editMatchBtn">විග්‍රහය සංස්කරණය</button><button class="outline-btn" id="printMatchBtn">පොරොන්දම් වාර්තාව මුද්‍රණය / පීඩීඑෆ්</button>';r.insertBefore(bar,r.firstChild);const editBtn=document.getElementById('editMatchBtn');editBtn.onclick=()=>{const active=r.classList.toggle('edit-active');r.querySelectorAll('.match-item div:last-child,.porondam-explain-card p,.note,.porondam-score-copy p').forEach(x=>x.contentEditable=active?'true':'false');editBtn.textContent=active?'සංස්කරණය අවසන්':'විග්‍රහය සංස්කරණය';};document.getElementById('printMatchBtn').onclick=()=>openMatchReport(d);};
function openMatchReport(d){const c=getSettings();const vcode=reportCode('HP');const w=window.open('','_blank');if(!w)return alert('නව කවුළුව විවෘත කිරීමට අවසර දෙන්න.');const pct=Math.round(d.score/d.out_of*100);const rows=d.factors.map((f,i)=>`<tr><td>${i+1}</td><td>${esc(f.name)}</td><td>${esc(f.grade)}</td><td>${esc(f.category||'')}</td><td>${esc(f.note)}</td></tr>`).join('');w.document.write(`<!doctype html><html lang="si"><head><meta charset="utf-8"><title>පොරොන්දම් වාර්තාව</title><style>@page{size:A4;margin:15mm}body{font-family:"Nirmala UI","Iskoola Pota",sans-serif;color:#2c1e20}.head{text-align:center;border-bottom:2px solid #7a2638;padding-bottom:8mm}.head h1{color:#7a2638}.meta{margin:6mm 0;line-height:1.8}.score{font-size:30px;color:#7a2638;font-weight:900}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #e6d8c8;padding:3mm}th{background:#f8efe5}.foot{margin-top:10mm;border-top:1px solid #ddd;padding-top:4mm;font-size:10px;color:#6f6265}.bar{display:flex;justify-content:flex-end;margin-bottom:6mm}.bar button{background:#7a2638;color:#fff;border:0;padding:10px 16px;border-radius:10px}@media print{.bar{display:none}}</style></head><body>${trialWatermarkHtml()}<div class="bar"><button onclick="window.print()">පීඩීඑෆ් ලෙස සුරකින්න / මුද්‍රණය</button></div><div class="head">${c.logo?`<img src="${c.logo}" style="max-height:22mm;max-width:50mm;object-fit:contain">`:''}<h1>${esc(c.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</h1>${c.astrologer?`<div>ජ්‍යෝතිෂ්‍යවේදී: ${esc(c.astrologer)}</div>`:''}<h2>පොරොන්දම් විග්‍රහ වාර්තාව</h2></div><div class="meta"><b>ස්ත්‍රී පාර්ශවය:</b> ${esc(d.bride_summary.name)} — ${esc(d.bride_summary.nakshatra.name)} / ${esc(d.bride_summary.moon_sign.name)}<br><b>පුරුෂ පාර්ශවය:</b> ${esc(d.groom_summary.name)} — ${esc(d.groom_summary.nakshatra.name)} / ${esc(d.groom_summary.moon_sign.name)}<br><span class="score">${pct}% — ${esc(d.verdict||'')}</span><br><b>වාර්තා සත්‍යාපන අංකය:</b> ${esc(vcode)}</div><table><thead><tr><th>අංකය</th><th>පොරොන්දම</th><th>තත්ත්වය</th><th>අංශය</th><th>විස්තරය</th></tr></thead><tbody>${rows}</tbody></table><div class="foot">${esc(d.note)}<br><br>${c.phone?`දුරකථන: ${esc(c.phone)} • `:''}${c.address?esc(c.address):''}${c.creator?`<br>පද්ධති නිර්මාණය: ${esc(c.creator)}`:''}<br>${esc(c.footer||'')}${c.signature?`<br><img src="${c.signature}" style="max-height:20mm;max-width:45mm;object-fit:contain;margin-top:5mm">`:''}${c.seal?`<br><img src="${c.seal}" style="max-height:18mm;max-width:42mm;object-fit:contain;margin-top:4mm">`:''}</div></body></html>`);w.document.close();}


// v2.4 — සුරැකි ජන්ම කේන්දර / විග්‍රහ / පොරොන්දම් සහ නව දර්ශන
(function(){
  // පැති මෙනුව සහ ප්‍රධාන ටැබ් එකට එකම සක්‍රීය තත්ත්වය
  document.querySelectorAll('.side-link[data-go]').forEach(b=>b.onclick=()=>{goTab(b.dataset.go);document.querySelectorAll('.side-link[data-go]').forEach(x=>x.classList.toggle('active',x===b));window.scrollTo({top:0,behavior:'smooth'});});
  document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{document.querySelectorAll('.side-link[data-go]').forEach(x=>x.classList.toggle('active',x.dataset.go===t.dataset.tab));}));

  const STORE='hela_jyotishya_saved_v24';
  const modal=document.getElementById('recordsModal');
  const openBtn=document.getElementById('savedBtn');
  const listEl=document.getElementById('recordList');
  const searchEl=document.getElementById('recordSearch');
  const filterEl=document.getElementById('recordFilter');
  const typeName={birth:'ජන්ම කේන්දරය',reference:'කේන්දර විග්‍රහය',match:'පොරොන්දම් විග්‍රහය'};
  const load=()=>{try{return JSON.parse(localStorage.getItem(STORE)||'[]')}catch(e){return []}};
  const persist=(a)=>{try{localStorage.setItem(STORE,JSON.stringify(a.slice(0,30)));dbMirrorSet(STORE,a.slice(0,30));return true}catch(e){alert('බ්‍රවුසර ගබඩාවේ ඉඩ ප්‍රමාණවත් නැත. පැරණි වාර්තාවක් මකා නැවත උත්සාහ කරන්න.');return false}};
  const titleFor=(type,input,result)=>{
    if(type==='match') return `${input?.bride?.name||'ස්ත්‍රී පාර්ශවය'} × ${input?.groom?.name||'පුරුෂ පාර්ශවය'}`;
    return input?.name || result?.person?.name || 'නම නොමැත';
  };
  function saveRecord(type,input,result){
    if(!result){alert('පළමුව ගණනය හෝ විග්‍රහය සකස් කරන්න.');return;}
    const a=load();
    const rec={id:String(Date.now()),type,title:titleFor(type,input,result),input,result,saved_at:new Date().toISOString()};
    a.unshift(rec); if(persist(a)){alert('වාර්තාව සාර්ථකව සුරකින ලදී.');renderRecords();}
  }
  function renderRecords(){
    if(!listEl)return;
    const q=(searchEl?.value||'').trim().toLowerCase(); const f=filterEl?.value||'all';
    const rows=load().filter(r=>(f==='all'||r.type===f)&&(!q||JSON.stringify(r).toLowerCase().includes(q)));
    listEl.innerHTML=rows.length?rows.map(r=>`<div class="record-row"><div><span class="record-type">${esc(typeName[r.type]||'වාර්තාව')}</span><b>${esc(r.title||'නම නොමැත')}</b><span>${new Date(r.saved_at).toLocaleString('si-LK')} • සුරැකි පිටපත</span></div><div class="record-actions"><button data-open="${r.id}">විවෘත කරන්න</button><button data-copy="${r.id}">පිටපතක් සාදන්න</button><button data-del="${r.id}">මකන්න</button></div></div>`).join(''):'<div class="note">සුරැකි වාර්තා නොමැත.</div>';
    listEl.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>openRecord(b.dataset.open));
    listEl.querySelectorAll('[data-copy]').forEach(b=>b.onclick=()=>{const a=load();const r=a.find(x=>x.id===b.dataset.copy);if(!r)return;const c=JSON.parse(JSON.stringify(r));c.id=String(Date.now());c.title=(c.title||'වාර්තාව')+' — පිටපත';c.saved_at=new Date().toISOString();a.unshift(c);persist(a);renderRecords();});
    listEl.querySelectorAll('[data-del]').forEach(b=>b.onclick=()=>{if(!confirm('මෙම සුරැකි වාර්තාව මකන්නද?'))return;persist(load().filter(x=>x.id!==b.dataset.del));renderRecords();});
  }
  function fillBirth(p){if(!p)return;$('#name').value=p.name||'';$('#date').value=p.birth_date||'';$('#time').value=p.birth_time||'';$('#lat').value=p.latitude??'';$('#lon').value=p.longitude??'';$('#tz').value=p.timezone_offset??5.5;}
  function fillReference(p){if(!p)return;$('#refName').value=p.name||'';$('#refDate').value=p.birth_date||'';$('#refTime').value=p.birth_time||'';$('#refLat').value=p.latitude??'';$('#refLon').value=p.longitude??'';$('#refTz').value=p.timezone_offset??5.5;}
  function fillPair(prefix,p){if(!p)return;const g=id=>document.getElementById(prefix+id);g('Name').value=p.name||'';g('Date').value=p.birth_date||'';g('Time').value=p.birth_time||'';g('Lat').value=p.latitude??'';g('Lon').value=p.longitude??'';g('Tz').value=p.timezone_offset??5.5;}
  function openRecord(id){const r=load().find(x=>x.id===id);if(!r)return;modal.classList.add('hidden');if(r.type==='birth'){goTab('birth');fillBirth(r.input);renderBirth(r.result);}else if(r.type==='reference'){goTab('reference');fillReference(r.input);renderReference(r.result);}else if(r.type==='match'){goTab('match');fillPair('groom',r.input?.groom);fillPair('bride',r.input?.bride);renderMatch(r.result);}window.scrollTo({top:0,behavior:'smooth'});}
  if(openBtn)openBtn.onclick=()=>{modal.classList.remove('hidden');renderRecords();};
  if(document.getElementById('recordsClose'))document.getElementById('recordsClose').onclick=()=>modal.classList.add('hidden');
  if(searchEl)searchEl.oninput=renderRecords;if(filterEl)filterEl.onchange=renderRecords;
  if(modal)modal.addEventListener('click',e=>{if(e.target===modal)modal.classList.add('hidden')});

  function deepPanel(result){
    const secs=result?.reading?.sections||[];
    const get=(needle)=>secs.find(s=>(s.title||'').includes(needle));
    const career=get('රැකියා')||get('වෘත්තීය'); const marriage=get('විවාහ'); const finance=get('මුදල්'); const foreign=get('විදේශ'); const remedies=secs.find(s=>(s.title||'').includes('පිළියම්')); const challenge=get('අභියෝග')||get('අපල');
    const examples=[career,marriage,foreign].filter(Boolean).slice(0,3);
    return `<div class="deep-v24"><div class="pro-section-label">විග්‍රහ සාරාංශය සහ ප්‍රායෝගික නිදසුන්</div><div class="deep-grid-v24">
      ${career?`<div class="deep-card-v24"><h4>රැකියා හා වෘත්තීය</h4><p>${esc(career.text)}</p></div>`:''}
      ${finance?`<div class="deep-card-v24"><h4>මුදල් හා ලාභ</h4><p>${esc(finance.text)}</p></div>`:''}
      ${marriage?`<div class="deep-card-v24"><h4>විවාහ හා සබඳතා</h4><p>${esc(marriage.text)}</p></div>`:''}
      ${foreign?`<div class="deep-card-v24"><h4>විදේශ ගමන්</h4><p>${esc(foreign.text)}</p></div>`:''}
      ${challenge?`<div class="deep-card-v24"><h4>අපල හා අභියෝග</h4><p>${esc(challenge.text)}</p></div>`:''}
      <div class="deep-card-v24"><h4>නිදසුන්</h4><ul>${examples.map(s=>`<li>${esc((s.text||'').split('උදාහරණයක් ලෙස,').slice(-1)[0].trim().slice(0,260))}</li>`).join('')||'<li>දශා සහ ගෝචර කාලය එකට සලකා සිදුවීම් කාලසීමාව තීරණය කරන්න.</li>'}</ul></div>
      ${remedies?`<div class="deep-card-v24 remedy"><h4>පිළියම් හා උපදෙස් — හේතුව සහ නිදසුන් සමඟ</h4><p>${esc(remedies.text)}</p></div>`:''}
      <div class="deep-card-v24"><h4>පිළියම් තෝරාගැනීමේ ක්‍රමය</h4><ul><li>පළමුව වත්මන් මහා දශාව, අතුරු දශාව සහ බලපාන භාවය හඳුනාගන්න.</li><li>බිය ඇති කරන හෝ අධික වියදම් ඉල්ලන පිළියම් අනිවාර්ය ලෙස නොගන්න.</li><li>උදාහරණය: ශනි කාලයක ප්‍රමාද තිබේ නම් පින්කමක් සමඟ විනය, කාලසටහන සහ ණය/බිල් නියමිත දිනට පාලනය කිරීමත් පිළියමේ කොටසක් ලෙස ගන්න.</li></ul></div>
    </div></div>`;
  }

  // වත්මන් render ක්‍රමවලට සුරැකීම සහ ගැඹුරු සාරාංශය එක් කරයි.
  const oldBirth=renderBirth; renderBirth=function(result){oldBirth(result);const c=$('#birthResults');const actions=c.querySelector('.actions-row');if(actions){const b=document.createElement('button');b.className='primary';b.textContent='කේන්දරය සුරකින්න';b.onclick=()=>saveRecord('birth',mainPayload(),result);actions.insertBefore(b,actions.firstChild);}c.insertAdjacentHTML('beforeend',deepPanel(result));};
  const oldRef=renderReference; renderReference=function(result){oldRef(result);const c=$('#refResults');const actions=c.querySelector('.actions-row');if(actions){const b=document.createElement('button');b.className='primary';b.textContent='විග්‍රහය සුරකින්න';b.onclick=()=>saveRecord('reference',referenceBirthPayload(),result);actions.insertBefore(b,actions.firstChild);}c.insertAdjacentHTML('beforeend',deepPanel(result));};
  const oldMatch2=renderMatch; renderMatch=function(result){oldMatch2(result);const c=$('#matchResults');let actions=c.querySelector('.porondam-actions');if(!actions){actions=document.createElement('div');actions.className='porondam-actions';c.insertBefore(actions,c.firstChild);}const b=document.createElement('button');b.className='primary';b.textContent='පොරොන්දම් වාර්තාව සුරකින්න';b.onclick=()=>saveRecord('match',{groom:payload('groom'),bride:payload('bride')},result);actions.insertBefore(b,actions.firstChild);};
})();


// 2.4.2 — ශීර්ෂ රූපයේ පෙනෙන මෙනු කොටස් සැබෑ මෙනු ක්‍රියා වලට සම්බන්ධ කිරීම.
(function(){
  document.querySelectorAll('[data-hero-go]').forEach(function(btn){
    btn.addEventListener('click',function(){
      const target=btn.getAttribute('data-hero-go');
      const tab=document.querySelector('.tab[data-tab="'+target+'"]');
      if(tab){tab.click();}
      document.querySelectorAll('.side-link[data-go]').forEach(function(x){x.classList.toggle('active',x.dataset.go===target);});
      const main=document.querySelector('.v24-content');
      if(main){main.scrollIntoView({behavior:'smooth',block:'start'});}
    });
  });
  const hs=document.getElementById('heroSettingsBtn');
  if(hs){hs.addEventListener('click',function(){const s=document.getElementById('settingsBtn');if(s)s.click();});}
})();


// v2.5 — ගනුදෙනුකරු කළමනාකරණය, වාර්තා ඉතිහාසය, හමුවීම්, මුහුර්ත, දරු නාම, ගෙවීම් සහ රිසිට්
(function(){
  const LS_CLIENTS='hela_clients_v25', LS_PAY='hela_payments_v25';
  const load=(k)=>{try{return JSON.parse(localStorage.getItem(k)||'[]')}catch(e){return []}};
  const save=(k,a)=>{localStorage.setItem(k,JSON.stringify(a));dbMirrorSet(k,a);};
  const byId=(id)=>document.getElementById(id);
  const openModal=(id)=>byId(id)?.classList.remove('hidden');
  const closeModal=(id)=>byId(id)?.classList.add('hidden');
  const reportStore=()=>{try{return JSON.parse(localStorage.getItem('hela_jyotishya_saved_v24')||'[]')}catch(e){return []}};
  const fmt=(d)=>{try{return new Date(d).toLocaleString('si-LK')}catch(e){return d||''}};
  let editingClientId='';

  function fillClient(c={}){
    editingClientId=c.id||'';
    const fields={clientName:c.name,clientPhone:c.phone,clientBirthDate:c.birth_date,clientBirthTime:c.birth_time,clientBirthPlace:c.birth_place,clientAddress:c.address,clientNextVisit:c.next_visit,clientNotes:c.notes};
    Object.entries(fields).forEach(([id,v])=>{const e=byId(id);if(e)e.value=v||'';});
  }
  function clientRecord(){return {id:editingClientId||String(Date.now()),name:byId('clientName').value.trim(),phone:byId('clientPhone').value.trim(),birth_date:byId('clientBirthDate').value,birth_time:byId('clientBirthTime').value,birth_place:byId('clientBirthPlace').value.trim(),address:byId('clientAddress').value.trim(),next_visit:byId('clientNextVisit').value,notes:byId('clientNotes').value.trim(),updated_at:new Date().toISOString()};}
  function linkedReports(c){const key=(c.name||'').trim().toLowerCase();return reportStore().filter(r=>key && JSON.stringify(r).toLowerCase().includes(key));}
  function renderClients(q=''){
    const list=byId('clientList'); if(!list)return;
    const rows=load(LS_CLIENTS).filter(c=>!q||JSON.stringify(c).toLowerCase().includes(q.toLowerCase()));
    list.innerHTML=rows.length?rows.map(c=>`<div class="record-row client-pro-row"><div><b>${esc(c.name||'නම නොමැත')}</b><span>${esc(c.phone||'දුරකථන නැත')} • ${esc(c.birth_date||'උපන් දිනය නැත')}</span>${c.next_visit?`<span>ඊළඟ හමුව: ${esc(c.next_visit)}</span>`:''}</div><div class="record-actions"><button data-client-open="${c.id}">විවෘත කරන්න</button><button data-client-use="${c.id}">කේන්දරයට යොදන්න</button><button data-client-del="${c.id}">මකන්න</button></div></div>`).join(''):'<div class="note">ගනුදෙනුකරු ගොනු නොමැත.</div>';
    list.querySelectorAll('[data-client-open]').forEach(b=>b.onclick=()=>showClient(b.dataset.clientOpen));
    list.querySelectorAll('[data-client-use]').forEach(b=>b.onclick=()=>{const c=load(LS_CLIENTS).find(x=>x.id===b.dataset.clientUse);if(!c)return;goTab('birth');$('#name').value=c.name||'';$('#date').value=c.birth_date||'';$('#time').value=c.birth_time||'';closeModal('clientsModal');});
    list.querySelectorAll('[data-client-del]').forEach(b=>b.onclick=()=>{if(!confirm('මෙම ගනුදෙනුකරු ගොනුව මකන්නද?'))return;save(LS_CLIENTS,load(LS_CLIENTS).filter(x=>x.id!==b.dataset.clientDel));renderClients(byId('clientSearch').value);});
  }
  function showClient(id){const c=load(LS_CLIENTS).find(x=>x.id===id);if(!c)return;fillClient(c);const reports=linkedReports(c);const detail=byId('clientDetail');detail.classList.remove('hidden');detail.innerHTML=`<div class="client-detail-head"><div><h3>${esc(c.name||'නම නොමැත')}</h3><p>${esc(c.phone||'')} ${c.address?'• '+esc(c.address):''}</p></div><div class="client-stat"><b>${reports.length}</b><span>සුරැකි වාර්තා</span><button class="outline-btn client-print-btn" id="clientPrintCurrent">ගොනුව මුද්‍රණය</button></div></div><div class="client-history-grid"><div class="client-history-card"><h4>වාර්තා ඉතිහාසය</h4>${reports.length?reports.slice(0,12).map(r=>`<div class="history-item"><b>${esc(r.type==='birth'?'ජන්ම කේන්දරය':r.type==='reference'?'කේන්දර විග්‍රහය':'පොරොන්දම්')}</b><span>${fmt(r.saved_at)}</span></div>`).join(''):'<p>මෙම නමට සම්බන්ධ සුරැකි වාර්තා නැත.</p>'}</div><div class="client-history-card"><h4>හමුවීම් සහ සටහන්</h4><p>${c.next_visit?`ඊළඟ හමුව: <b>${esc(c.next_visit)}</b>`:'ඊළඟ හමුවක් සටහන් කර නැත.'}</p><p>${esc(c.notes||'පුද්ගලික සටහන් නැත.')}</p></div></div>`;}
  byId('clientsBtn').onclick=()=>{openModal('clientsModal');renderClients('');};
  byId('clientsClose').onclick=()=>closeModal('clientsModal');
  byId('clientSearch').oninput=e=>renderClients(e.target.value);
  byId('clientNew').onclick=()=>{fillClient({});byId('clientDetail').classList.add('hidden');};
  byId('clientSave').onclick=()=>{const c=clientRecord();if(!c.name)return alert('නම ඇතුළත් කරන්න.');let a=load(LS_CLIENTS);const i=a.findIndex(x=>x.id===c.id);if(i>=0)a[i]=c;else a.unshift(c);save(LS_CLIENTS,a.slice(0,1000));editingClientId=c.id;renderClients(byId('clientSearch').value);showClient(c.id);};

  // මුහුර්ත හා සුභ කාල — උපන් විස්තර වලින් පුද්ගලික දත්ත ස්වයංක්‍රීයව ගණනය කරයි
  if(byId('muhurtaCity')) byId('muhurtaCity').innerHTML=cityOptions();
  if(byId('muhurtaNatalCity')) byId('muhurtaNatalCity').innerHTML=cityOptions();
  if(byId('muhurtaPartnerCity')) byId('muhurtaPartnerCity').innerHTML=cityOptions();
  if(byId('babyCity')) byId('babyCity').innerHTML=cityOptions();
  const today=new Date().toISOString().slice(0,10);
  if(byId('muhurtaFrom'))byId('muhurtaFrom').value=today;
  if(byId('muhurtaTo')){const d=new Date();d.setDate(d.getDate()+14);byId('muhurtaTo').value=d.toISOString().slice(0,10);}
  byId('muhurtaBtn').onclick=()=>openModal('muhurtaModal');
  byId('muhurtaClose').onclick=()=>closeModal('muhurtaModal');
  const muhurtaGrade=(s)=>s>=82?'ඉතා යෝග්‍ය':s>=70?'යෝග්‍ය':s>=58?'මධ්‍යම':s>=45?'අවධානයෙන්':'වළක්වා ගැනීම හොඳයි';

  function birthFromInputs(prefix){
    const date=byId(prefix+'Date')?.value||'', time=byId(prefix+'Time')?.value||'';
    if(!date||!time) return null;
    const city=cities[+(byId(prefix+'City')?.value||0)]||cities[0];
    return {name:byId(prefix+'Name')?.value||byId(prefix+'Label')?.value||'',birth_date:date,birth_time:time,birth_place:city[0],latitude:city[1],longitude:city[2],timezone_offset:city[3]};
  }
  async function autoBirthProfile(prefix){
    const birth=birthFromInputs(prefix); if(!birth) return null;
    return await post('/api/calculate',birth);
  }
  function profileText(title,r){
    if(!r)return '';
    return `<div class="auto-profile-person"><b>${esc(title)}</b><span>ලග්නය: ${esc(r.lagna?.rashi?.name||'—')}</span><span>චන්ද්‍ර රාශිය: ${esc(r.moon_sign?.name||'—')}</span><span>ජන්ම නැකත: ${esc(r.birth_nakshatra?.name||'—')} • ${esc(r.birth_nakshatra?.pada||'—')} වන පාදය</span></div>`;
  }
  let muhurtaNatalPreview=null, muhurtaPartnerPreview=null, babyPreview=null;
  async function refreshAutoPreview(prefix,targetId,title,slot){
    try{
      const r=await autoBirthProfile(prefix); if(!r)return;
      if(slot==='natal')muhurtaNatalPreview=r; else if(slot==='partner')muhurtaPartnerPreview=r; else if(slot==='baby')babyPreview=r;
      if(targetId==='muhurtaAutoProfile'){
        const html=`${profileText('ප්‍රධාන පුද්ගලයා',muhurtaNatalPreview)}${profileText('දෙවන පාර්ශවය',muhurtaPartnerPreview)}`;
        byId(targetId).innerHTML=html||'උපන් විස්තර දුන්නාම නැකත, පාදය, චන්ද්‍ර රාශිය සහ ලග්නය මෙහි ස්වයංක්‍රීයව පෙන්වයි.';
      }else{
        byId(targetId).innerHTML=profileText(title,r);
      }
    }catch(e){ /* incomplete input while typing — ignore */ }
  }
  [['muhurtaNatal','muhurtaAutoProfile','ප්‍රධාන පුද්ගලයා','natal'],['muhurtaPartner','muhurtaAutoProfile','දෙවන පාර්ශවය','partner'],['baby','babyAutoProfile','දරුවා','baby']].forEach(([prefix,target,title,slot])=>{
    ['Date','Time','City'].forEach(suf=>{const el=byId(prefix+suf);if(el)el.addEventListener('change',()=>refreshAutoPreview(prefix,target,title,slot));});
  });
  function toggleEditable(el,btn){
    const editing=el.getAttribute('contenteditable')==='true';
    el.setAttribute('contenteditable', editing?'false':'true');
    el.classList.toggle('is-editing',!editing);
    btn.textContent=editing?'ප්‍රතිඵල සංස්කරණය':'සංස්කරණය අවසන්';
    if(!editing) el.focus();
  }
  function printableWindow(title,body,subtitle=''){
    const cfg=getSettings(),w=window.open('','_blank');if(!w)return alert('නව කවුළුව විවෘත කිරීමට අවසර දෙන්න.');
    w.document.write(`<!doctype html><html lang="si"><head><meta charset="utf-8"><title>${esc(title)}</title><style>@page{size:A4;margin:14mm}body{font-family:"Nirmala UI","Iskoola Pota",sans-serif;color:#211b1c;background:#fff;margin:0}.bar{text-align:right;margin-bottom:7mm}.bar button{border:0;border-radius:10px;padding:10px 16px;background:#6c2437;color:#fff;font-weight:800}.cover{border:1.5px solid #c7a96a;border-radius:20px;padding:10mm;margin-bottom:7mm;background:linear-gradient(145deg,#fffdf8,#fbf4e8)}.cover h1{margin:0;color:#6c2437;font-size:26px}.cover p{margin:3mm 0 0;color:#695d60}.brand{font-weight:900;color:#8d6a2a;margin-bottom:3mm}.content{line-height:1.7}.muhurta-pro-card,.name-result-card,.note,.auto-profile-note{break-inside:avoid;border:1px solid #e5d8c5;border-radius:14px;padding:5mm;margin:0 0 4mm;background:#fffdf9}.muhurta-pro-head{display:flex;gap:5mm;align-items:center}.muhurta-rank{font-size:22px;font-weight:900;color:#8d6a2a}.muhurta-main{flex:1}.muhurta-main b,.muhurta-main strong,.muhurta-main span{display:block}.muhurta-score-ring{font-size:18px;font-weight:900;color:#6c2437}.muhurta-panchanga,.muhurta-time-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2mm;margin-top:3mm}.muhurta-panchanga span,.muhurta-time-grid span{border:1px solid #eee0cc;border-radius:8px;padding:2.5mm;font-size:10px}.muhurta-reasons{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin-top:3mm}.muhurta-reasons p{margin:1mm 0}.name-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:3mm}.name-result-card h4{margin:0 0 2mm;color:#6c2437}.name-meta{font-size:10px;color:#75696c}.footer{margin-top:8mm;border-top:1px solid #ddd0bc;padding-top:4mm;font-size:10px;color:#716568}.settings-actions,.record-actions,.muhurta-grade{display:none!important}@media print{.bar{display:none}}</style></head><body>${trialWatermarkHtml()}<div class="bar"><button onclick="print()">මුද්‍රණය / පීඩීඑෆ්</button></div><div class="cover"><div class="brand">${esc(cfg.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</div><h1>${esc(title)}</h1><p>${esc(subtitle)}</p><p><b>වාර්තා සත්‍යාපන අංකය:</b> ${esc(vcode)}</p></div><div class="content">${body}</div><div class="footer">${cfg.astrologer?`ජ්‍යෝතිෂ්‍යවේදී: ${esc(cfg.astrologer)}<br>`:''}${esc(cfg.address||'')} ${cfg.phone?` • ${esc(cfg.phone)}`:''}<br>${esc(cfg.footer||'')}${cfg.signature?`<br><img src="${cfg.signature}" style="max-height:18mm;max-width:42mm;object-fit:contain;margin-top:4mm">`:''}${cfg.seal?`<br><img src="${cfg.seal}" style="max-height:18mm;max-width:42mm;object-fit:contain;margin-top:4mm">`:''}</div></body></html>`);w.document.close();
  }

  byId('muhurtaGenerate').onclick=async()=>{
    const out=byId('muhurtaResults');out.innerHTML='<div class="note">දින, වේලා සහ පුද්ගලික කේන්දර ගැලපීම පරීක්ෂා කරමින්...</div>';
    const a=byId('muhurtaFrom').value,b=byId('muhurtaTo').value;if(!a||!b||a>b)return out.innerHTML='<div class="note">දිනයන් නිවැරදි කරන්න.</div>';
    const city=cities[+byId('muhurtaCity').value||0];
    try{
      const natal=await autoBirthProfile('muhurtaNatal');
      const partner=await autoBirthProfile('muhurtaPartner');
      byId('muhurtaAutoProfile').innerHTML=(natal||partner)?`${profileText('ප්‍රධාන පුද්ගලයා',natal)}${profileText('දෙවන පාර්ශවය',partner)}`:'පුද්ගලික උපන් විස්තර නොදුන් බැවින් සාමාන්‍ය පංචාංග පෙරහන් කිරීම භාවිතා වේ.';
      const data={purpose:byId('muhurtaPurpose').value,from_date:a,to_date:b,latitude:city[1],longitude:city[2],timezone_offset:city[3],natal_nakshatra_index:natal?.birth_nakshatra?.index??'',natal_moon_sign_index:natal?.moon_sign?.index??'',partner_nakshatra_index:partner?.birth_nakshatra?.index??'',partner_moon_sign_index:partner?.moon_sign?.index??''};
      const r=await post('/api/muhurta',data);const rows=r.results||[];
      const personalSummary=natal?`<div class="muhurta-summary"><b>පුද්ගලික ගැලපීම ස්වයංක්‍රීයව එක් කර ඇත</b><span>${esc(natal.person?.name||'ප්‍රධාන පුද්ගලයා')} — ${esc(natal.birth_nakshatra.name)} ${natal.birth_nakshatra.pada} පාදය • ${esc(natal.moon_sign.name)}${partner?` | ${esc(partner.person?.name||'දෙවන පාර්ශවය')} — ${esc(partner.birth_nakshatra.name)} ${partner.birth_nakshatra.pada} පාදය • ${esc(partner.moon_sign.name)}`:''}</span></div>`:'';
      out.innerHTML=`<div class="muhurta-summary"><b>${esc(r.purpose)}</b><span>${esc(r.note||'')}</span></div>${personalSummary}${rows.length?rows.map((x,i)=>`<div class="muhurta-pro-card"><div class="muhurta-pro-head"><div class="muhurta-rank">${i+1}</div><div class="muhurta-main"><b>${esc(x.date)} • ${esc(x.vara)}</b><strong>${esc(x.start)} – ${esc(x.end)}</strong><span>ලග්නය: ${esc(x.lagna)} • චන්ද්‍ර රාශිය: ${esc(x.moon_sign)} • හෝරාව: ${esc(x.hora||'—')}</span></div><div class="muhurta-score-ring"><b>${x.score}</b><span>/100</span></div></div><div class="muhurta-grade ${x.score>=70?'good':x.score>=58?'mid':'bad'}">${esc(x.label||muhurtaGrade(x.score))}</div><div class="muhurta-panchanga"><span>නැකත <b>${esc(x.nakshatra)}</b></span><span>තිථිය <b>${esc(x.tithi)}</b></span><span>යෝගය <b>${esc(x.yoga)}</b></span><span>කරණය <b>${esc(x.karana)}</b></span></div><div class="muhurta-time-grid"><span>උදාව ${esc(x.sunrise)}</span><span>අස්තය ${esc(x.sunset)}</span><span>රාහු ${esc(x.rahu?.join('–')||'—')}</span><span>යමගණ්ඩ ${esc(x.yama?.join('–')||'—')}</span><span>ගුලික ${esc(x.gulika?.join('–')||'—')}</span><span>අභිජිත් ${esc(x.abhijit?.join('–')||'—')}</span></div><div class="muhurta-reasons">${x.good?.length?`<div class="reason-good"><b>හොඳ කරුණු</b>${x.good.map(v=>`<p>✓ ${esc(v)}</p>`).join('')}</div>`:''}${x.caution?.length?`<div class="reason-warn"><b>අවධානය</b>${x.caution.map(v=>`<p>• ${esc(v)}</p>`).join('')}</div>`:''}${x.avoid?.length?`<div class="reason-bad"><b>වළක්වාගත යුතු කරුණු</b>${x.avoid.map(v=>`<p>! ${esc(v)}</p>`).join('')}</div>`:''}</div></div>`).join(''):'<div class="note">මෙම කාල පරාසයට සුදුසු ප්‍රතිඵල හමු නොවීය.</div>'}`;
      out.setAttribute('contenteditable','false');out.classList.remove('is-editing');byId('muhurtaEdit').textContent='ප්‍රතිඵල සංස්කරණය';
    }catch(e){out.innerHTML=`<div class="note">${esc(e.message||'ගණනයේ දෝෂයක් ඇතිවිය.')}</div>`;}
  };
  byId('muhurtaEdit').onclick=()=>toggleEditable(byId('muhurtaResults'),byId('muhurtaEdit'));
  byId('muhurtaPrint').onclick=()=>printableWindow('මුහුර්ත හා සුභ කාල වාර්තාව',byId('muhurtaResults').innerHTML,`${byId('muhurtaPurpose').value} • ${byId('muhurtaFrom').value} සිට ${byId('muhurtaTo').value} දක්වා`);

  // දරු නාම — නැකත/පාදය අනුව ප්‍රධාන ශබ්දය + විකල්ප ශබ්ද තෝරා, එම ශබ්ද වලින් නවීන නාම යෝජනා
  const syll=[['චු','චේ','චෝ','ලා'],['ලි','ලු','ලේ','ලෝ'],['අ','ඊ','උ','ඒ'],['ඔ','වා','වි','වු'],['වේ','වෝ','කා','කි'],['කු','ඝ','ඞ','ච'],['කේ','කෝ','හා','හි'],['හු','හේ','හෝ','ඩා'],['ඩි','ඩු','ඩේ','ඩෝ'],['මා','මි','මු','මේ'],['මෝ','ටා','ටි','ටු'],['ටේ','ටෝ','පා','පි'],['පු','ෂ','ණ','ඨ'],['පේ','පෝ','රා','රි'],['රු','රේ','රෝ','තා'],['ති','තු','තේ','තෝ'],['නා','නි','නු','නේ'],['නෝ','යා','යි','යු'],['යේ','යෝ','භා','භි'],['භු','ධා','ඵා','ඪා'],['භේ','භෝ','ජා','ජි'],['ජු','ජේ','ජෝ','ඛි'],['ගා','ගි','ගු','ගේ'],['ගෝ','සා','සි','සු'],['සේ','සෝ','දා','දි'],['දු','ථ','ඣ','ඤ'],['දේ','දෝ','චා','චි']];
  const modernNames=[
    {n:'අහස්',g:'male',o:'sri',m:'අහස; විවෘතභාවය සහ උසස් අරමුණු'}, {n:'අරින්',g:'male',o:'sri',m:'ශක්තිමත් හා නවීන හඬක් ඇති නාමයක්'}, {n:'අමායා',g:'female',o:'sri',m:'මෘදු හා සුන්දර හැඟීමක් දෙන නාමයක්'}, {n:'අනුකි',g:'female',o:'sri',m:'කරුණාව සහ මෘදුභාවය සංකේතවත් කරන නවීන නාමයක්'},
    {n:'කවිඳු',g:'male',o:'sri',m:'කවියන්ගේ සඳ; කලාත්මකභාවය'}, {n:'කෙනුල්',g:'male',o:'sri',m:'නවීන ශ්‍රී ලාංකික භාවිතයේ ජනප්‍රිය කෙටි නාමයක්'}, {n:'කිහාරා',g:'female',o:'sri',m:'සංගීතමය හා මෘදු හඬක් ඇති නවීන නාමයක්'}, {n:'සෙනුලි',g:'female',o:'sri',m:'මෘදුභාවය සහ ආලෝකමත් හැඟීම'},
    {n:'සවිඳු',g:'male',o:'sri',m:'ශක්තිය හා දක්ෂතාවය යන අදහස් සමඟ භාවිත වන නාමයක්'}, {n:'සනුකි',g:'female',o:'sri',m:'නවීන, සරල සහ මෘදු නාමයක්'}, {n:'විහඟ',g:'male',o:'sri',m:'පක්ෂියා; නිදහස'}, {n:'විහාරා',g:'female',o:'sri',m:'ශාන්තභාවය සහ පූජනීය ස්ථානය'},
    {n:'රිවින්',g:'male',o:'sri',m:'නවීන කෙටි නාමයක්; දීප්තිමත් හඬක්'}, {n:'රිහන්සා',g:'female',o:'sri',m:'මෘදු හා අලංකාර නවීන නාමයක්'}, {n:'දිනාල්',g:'male',o:'sri',m:'ජය සහ දීප්තිය යන අදහස් සමඟ භාවිත වන නාමයක්'}, {n:'දිනාරා',g:'female',o:'sri',m:'දීප්තිය සහ සෞන්දර්යය සංකේතවත් කරන නවීන නාමයක්'},
    {n:'ආරව්',g:'male',o:'indian',m:'සාමකාමී හඬක්; නවීන ඉන්දියානු නාමයක්'}, {n:'අද්වයිත්',g:'male',o:'indian',m:'එකම, දෙකක් නොවන'}, {n:'ආන්වි',g:'female',o:'indian',m:'දේවී සම්බන්ධ නාමයක් ලෙස භාවිත වේ'}, {n:'ආද්‍යා',g:'female',o:'indian',m:'මුල්ම, ප්‍රථම'},
    {n:'විහාන්',g:'male',o:'indian',m:'උදෑසන; නව ආරම්භය'}, {n:'කියාන්',g:'male',o:'indian',m:'කෘපාව / රාජකීයත්වය යන අර්ථ සමඟ භාවිත වේ'}, {n:'මිරායා',g:'female',o:'indian',m:'නවීන ඉන්දියානු නාම භාවිතයක්'}, {n:'නයිරා',g:'female',o:'indian',m:'දීප්තිමත්, බැබළෙන යන අර්ථ සමඟ භාවිත වේ'},
    {n:'රෙයාන්',g:'male',o:'indian',m:'සුවඳවත් පැළෑටිය / ස්වර්ගීය යන අර්ථ සමඟ විවිධ සංස්කෘතික භාවිත ඇත'}, {n:'රිවා',g:'female',o:'indian',m:'ගලා යන ජලය / නර්මදා නදිය සම්බන්ධ නාම භාවිතයක්'},
    {n:'ලියෝ',g:'male',o:'global',m:'සිංහයා; ධෛර්යය'}, {n:'නෝවා',g:'male',o:'global',m:'විවේකය, සැනසීම යන අර්ථ සමඟ බයිබල් සම්ප්‍රදායේ භාවිත වේ'}, {n:'ලූකා',g:'male',o:'global',m:'ආලෝකය සමඟ සම්බන්ධ යුරෝපීය නාම පවුලක්'}, {n:'එලියෝ',g:'male',o:'global',m:'සූර්යයා/ආලෝකය සමඟ සම්බන්ධ නවීන යුරෝපීය නාමයක්'},
    {n:'ලූනා',g:'female',o:'global',m:'චන්ද්‍රයා'}, {n:'මියා',g:'female',o:'global',m:'මගේ / ආදරණීය යන අදහස් සමඟ විවිධ භාෂාවල භාවිත වේ'}, {n:'ආරියා',g:'female',o:'global',m:'මහත්, ගෞරවනීය යන අර්ථ සමඟ විවිධ සංස්කෘතික භාවිත ඇත'}, {n:'එලා',g:'female',o:'global',m:'ආලෝකය හෝ සුන්දරත්වය සමඟ සම්බන්ධ අර්ථ විවිධ භාෂාවල ඇත'},
    {n:'නෝරා',g:'female',o:'global',m:'ගෞරවය / ආලෝකය යන අර්ථ සමඟ භාවිත වන නාමයක්'}, {n:'කයි',g:'male',o:'global',m:'විවිධ සංස්කෘතිවල මුහුද, ජය හෝ රැකවරණය වැනි අර්ථ ඇත'}, {n:'මයිලෝ',g:'male',o:'global',m:'මෘදු, මිත්‍රශීලී හඬක් ඇති නවීන නාමයක්'}, {n:'අයිලා',g:'female',o:'global',m:'චන්ද්‍ර ආලෝකය / දූපත යන අර්ථ විවිධ භාෂාවල ඇත'},
    {n:'සෝයා',g:'female',o:'global',m:'ජීවිතය'}, {n:'ඒඩන්',g:'male',o:'global',m:'කුඩා ගිනිදැල් / උණුසුම යන අර්ථ සමඟ කෙල්ටික් භාවිතයක්'}, {n:'එවන්',g:'male',o:'global',m:'දෙවියන්ගේ කරුණාව යන අර්ථ සමඟ වේල්ස් නාම භාවිතයක්'}, {n:'සියා',g:'female',o:'global',m:'ජය / ආලෝකය යන අර්ථ සමඟ විවිධ භාවිත ඇත'}
  ];
  const originLabel={sri:'ශ්‍රී ලාංකික නවීන',indian:'ඉන්දියානු නවීන',global:'ජාත්‍යන්තර නවීන',creative:'නිර්මාණාත්මක නවීන'};
  const creativeEndings={
    male:['වින්','හන්','යොන්','රු','න්','ත්','ෂාන්','දීව්'],
    female:['යා','නි','රා','ශා','ලි','නා','මි','කා']
  };
  function cleanSyl(x){return String(x||'').trim();}
  function initialCluster(x){
    const s=cleanSyl(x); if(!s)return '';
    const marks='ාැෑිීුූෘෙේෛොෝෞංඃ්';
    let out=''; for(const ch of s){ if(!marks.includes(ch))out+=ch; if(out.length>=1)break; }
    return out||s[0];
  }
  function suggestedSyllables(all,primary){
    const out=[cleanSyl(primary),...(all||[]).map(cleanSyl)];
    const first=initialCluster(primary);
    const near=(all||[]).filter(x=>initialCluster(x)===first);
    return [...new Set([...out,...near].filter(Boolean))].slice(0,6);
  }
  function exactStarts(name,syl){return cleanSyl(name).startsWith(cleanSyl(syl));}
  function relatedStarts(name,syl){const a=initialCluster(name),b=initialCluster(syl);return !!a&&a===b;}
  function createNamesFromSyllable(syl,gender,style){
    if(style!=='all' && style!=='sri') return [];
    const gs=gender==='all'?['male','female']:[gender], out=[];
    gs.forEach(g=>creativeEndings[g].forEach((end,i)=>{
      const n=(cleanSyl(syl)+end).replace(/(.)\1+/g,'$1');
      if(n.length>=3)out.push({n,g,o:'creative',m:'තෝරාගත් නාම ශබ්දයෙන් සකස් කළ නවීන නිර්මාණාත්මක නාම යෝජනාවකි. නාම මූලාශ්‍ර අර්ථයක් ලෙස නොසලකන්න.',score:88-i});
    }));
    return out;
  }
  function selectedNames(syllables,style,gender){
    const ss=[...new Set((syllables||[]).map(cleanSyl).filter(Boolean))];
    let rows=modernNames.filter(x=>(style==='all'||x.o===style)&&(gender==='all'||x.g===gender)).map(x=>{
      let score=20, matched='';
      for(const s of ss){if(exactStarts(x.n,s)){score=100;matched=s;break;}if(score<80&&relatedStarts(x.n,s)){score=80;matched=s;}}
      return {...x,score,matched};
    });
    ss.forEach(s=>rows.push(...createNamesFromSyllable(s,gender,style).map(x=>({...x,matched:s}))));
    const seen=new Set();
    return rows.filter(x=>{const k=x.n+'|'+x.g;if(seen.has(k))return false;seen.add(k);return true;}).sort((a,b)=>b.score-a.score||a.n.localeCompare(b.n)).slice(0,24);
  }
  function renderNameCards(names){
    return names.length?`<div class="name-grid">${names.map(x=>`<div class="name-result-card"><h4>${esc(x.n)}</h4><div class="name-meta">${esc(originLabel[x.o]||'නවීන')} • ${x.g==='male'?'පුරුෂ':'ස්ත්‍රී'}${x.matched?` • <b>${esc(x.matched)}</b> ශබ්දයෙන්`:''}${x.score>=100?' • සෘජු ගැලපීම':x.score>=80?' • ශබ්ද ගැලපීම':''}</div><p>${esc(x.m)}</p></div>`).join('')}</div>`:`<div class="note">තෝරාගත් ශබ්දයට සහ පෙරහන්වලට ගැලපෙන නාම හමු නොවීය. වෙනත් ශබ්දයක් හෝ “සියලු වර්ග” තෝරන්න.</div>`;
  }
  function installNameSyllableControls(state){
    document.querySelectorAll('[data-name-syl]').forEach(btn=>btn.onclick=()=>{
      btn.classList.toggle('active');
      const chosen=[...document.querySelectorAll('[data-name-syl].active')].map(x=>x.dataset.nameSyl);
      if(!chosen.length){btn.classList.add('active');return;}
      const holder=byId('babyGeneratedNames'); if(holder)holder.innerHTML=renderNameCards(selectedNames(chosen,state.style,state.gender));
      const chosenText=byId('babyChosenSounds'); if(chosenText)chosenText.textContent=chosen.join(' • ');
    });
  }
  byId('babyNameBtn').onclick=()=>openModal('babyNameModal');
  byId('babyNameClose').onclick=()=>closeModal('babyNameModal');
  byId('babyNameGenerate').onclick=async()=>{
    const out=byId('babyNameResults');out.innerHTML='ජන්ම නැකත, පාදය සහ නාම ශබ්ද ගණනය කරමින්...';
    try{
      const r=await autoBirthProfile('baby');
      if(!r)throw new Error('උපන් දිනය සහ උපන් වෙලාව ඇතුළත් කරන්න.');
      const n=r.birth_nakshatra.index,p=Number(r.birth_nakshatra.pada)-1,primary=syll[n]?.[p]||'—',all=syll[n]||[];
      const choices=suggestedSyllables(all,primary),style=byId('babyStyle').value,gender=byId('babyGender').value;
      const defaultChosen=choices.slice(0,Math.min(4,choices.length));
      const names=selectedNames(defaultChosen,style,gender);
      byId('babyAutoProfile').innerHTML=profileText(byId('babyLabel').value||'දරුවා',r);
      out.innerHTML=`<div class="baby-profile-result"><h3>${esc(r.birth_nakshatra.name)} • ${r.birth_nakshatra.pada} වන පාදය</h3><p>චන්ද්‍ර රාශිය: <b>${esc(r.moon_sign.name)}</b> • ලග්නය: <b>${esc(r.lagna.rashi.name)}</b></p><p>ප්‍රධාන නාම ආරම්භක ශබ්දය: <b class="name-syllable">${esc(primary)}</b></p><p><b>අමතර යෝජිත ශබ්ද:</b> ${choices.filter(x=>x!==primary).map(esc).join(' • ')||'—'}</p></div>
      <div class="subsection-title">නාමයට භාවිත කරන ශබ්ද තෝරන්න</div>
      <div class="name-syllable-picker">${choices.map((x,i)=>`<button type="button" class="syll-chip name-choice ${defaultChosen.includes(x)?'active':''}" data-name-syl="${esc(x)}">${i===0?'★ ':''}${esc(x)}</button>`).join('')}</div>
      <div class="note">ප්‍රධාන ශබ්දය ★ ලෙස පෙන්වයි. අමතර ශබ්ද එකක් හෝ කිහිපයක් තෝරා නාම ලැයිස්තුව නැවත සකස් කළ හැක. දැනට තෝරා ඇති ශබ්ද: <b id="babyChosenSounds">${defaultChosen.map(esc).join(' • ')}</b></div>
      <div class="subsection-title">තෝරාගත් ශබ්ද වලින් නවීන නාම යෝජනා</div><div id="babyGeneratedNames">${renderNameCards(names)}</div>
      <div class="note">නැකත්-පාද ශබ්ද යනු සම්ප්‍රදායික නාම ආරම්භක මාර්ගෝපදේශයකි. “නිර්මාණාත්මක නවීන” ලෙස සලකුණු කළ නාම පද්ධතිය විසින් ශබ්දයෙන් සකස් කරන යෝජනා වන අතර ඒවාට පැරණි භාෂාමය අර්ථයක් අනිවාර්යයෙන්ම නොමැත. අවසාන නම තෝරන විට උච්චාරණය, වාසගම සහ අර්ථයත් සලකා බලන්න.</div>`;
      out.setAttribute('contenteditable','false');out.classList.remove('is-editing');byId('babyNameEdit').textContent='ප්‍රතිඵල සංස්කරණය';
      installNameSyllableControls({style,gender});
    }catch(e){out.innerHTML=`<div class="note">${esc(e.message||'ගණනයේ දෝෂයක් ඇතිවිය.')}</div>`;}
  };
  byId('babyNameEdit').onclick=()=>toggleEditable(byId('babyNameResults'),byId('babyNameEdit'));
  byId('babyNamePrint').onclick=()=>printableWindow('දරු නාම සහ නාම අක්ෂර වාර්තාව',byId('babyNameResults').innerHTML,byId('babyLabel').value||'ජන්ම නැකත අනුව නාම යෝජනා');

  // ගෙවීම් හා රිසිට්
  byId('paymentsBtn').onclick=()=>{openModal('paymentsModal');renderPayments();};byId('paymentsClose').onclick=()=>closeModal('paymentsModal');if(byId('payDate'))byId('payDate').value=today;
  function payData(){return{id:String(Date.now()),client:byId('payClient').value.trim(),service:byId('payService').value,amount:+byId('payAmount').value||0,status:byId('payStatus').value,date:byId('payDate').value,receipt:byId('payReceipt').value.trim()||('R-'+Date.now().toString().slice(-7))};}
  function renderPayments(){const el=byId('paymentList');const rows=load(LS_PAY);el.innerHTML=rows.length?rows.slice(0,30).map(x=>`<div class="record-row"><div><b>${esc(x.receipt)} • ${esc(x.client||'නම නොමැත')}</b><span>${esc(x.service)} • රු. ${Number(x.amount).toLocaleString()} • ${esc(x.status)} • ${esc(x.date)}</span></div><div class="record-actions"><button data-pay-print="${x.id}">රිසිට්</button></div></div>`).join(''):'<div class="note">ගෙවීම් සටහන් නොමැත.</div>';el.querySelectorAll('[data-pay-print]').forEach(b=>b.onclick=()=>{const x=load(LS_PAY).find(v=>v.id===b.dataset.payPrint);if(x)printReceipt(x);});}
  byId('paySave').onclick=()=>{const x=payData();const a=load(LS_PAY);a.unshift(x);save(LS_PAY,a);byId('payReceipt').value=x.receipt;renderPayments();};byId('payPrint').onclick=()=>printReceipt(payData());
  function printReceipt(x){const c=getSettings(),w=window.open('','_blank');if(!w)return alert('නව කවුළුව විවෘත කිරීමට අවසර දෙන්න.');w.document.write(`<!doctype html><html lang="si"><head><meta charset="utf-8"><title>රිසිට්</title><style>@page{size:A5;margin:14mm}body{font-family:"Nirmala UI","Iskoola Pota",sans-serif;color:#211b1c}.r{border:2px solid #8e6a2b;border-radius:18px;padding:12mm}.h{text-align:center;border-bottom:1px solid #d9c7a4;padding-bottom:6mm}.h h1{margin:0;color:#6d2638}.row{display:flex;justify-content:space-between;border-bottom:1px dashed #ddd;padding:4mm 0}.total{font-size:24px;font-weight:900;color:#6d2638}.foot{margin-top:8mm;font-size:10px;color:#666}.bar{text-align:right;margin-bottom:6mm}@media print{.bar{display:none}}</style></head><body>${trialWatermarkHtml()}<div class="bar"><button onclick="print()">මුද්‍රණය</button></div><div class="r"><div class="h">${c.logo?`<img src="${c.logo}" style="max-height:18mm">`:''}<h1>${esc(c.institute||'හෙළ ජ්‍යෝතිෂ්‍ය ආයතනය')}</h1><div>ගෙවීම් රිසිට්</div></div><div class="row"><b>රිසිට් අංකය</b><span>${esc(x.receipt)}</span></div><div class="row"><b>දිනය</b><span>${esc(x.date)}</span></div><div class="row"><b>ගනුදෙනුකරු</b><span>${esc(x.client)}</span></div><div class="row"><b>සේවාව</b><span>${esc(x.service)}</span></div><div class="row"><b>තත්ත්වය</b><span>${esc(x.status)}</span></div><div class="row total"><b>මුදල</b><span>රු. ${Number(x.amount).toLocaleString()}</span></div><div class="foot">${c.phone?`දුරකථන: ${esc(c.phone)}<br>`:''}${esc(c.address||'')}<br>${esc(c.footer||'')}</div></div></body></html>`);w.document.close();}

  ['clientsModal','muhurtaModal','babyNameModal','paymentsModal'].forEach(id=>{const m=byId(id);if(m)m.addEventListener('click',e=>{if(e.target===m)closeModal(id);});});
})();


// v3.2 — සම්පූර්ණ වාර්තා මධ්‍යස්ථානය
(function(){
 const btn=document.getElementById('reportCenterBtn'), modal=document.getElementById('reportCenterModal'); if(!btn||!modal)return;
 const close=()=>modal.classList.add('hidden'); btn.onclick=()=>modal.classList.remove('hidden'); document.getElementById('reportCenterClose').onclick=close; modal.addEventListener('click',e=>{if(e.target===modal)close()});
 const map={saved:'savedBtn',clients:'clientsBtn',muhurta:'muhurtaBtn',baby:'babyNameBtn',payments:'paymentsBtn'};
 modal.querySelectorAll('[data-open-panel]').forEach(x=>x.onclick=()=>{close();const id=map[x.dataset.openPanel];document.getElementById(id)?.click();});
})();


// v3.3 — backup / restore UI
(function(){
  const btn=document.getElementById('dataBackupBtn'), modal=document.getElementById('dataBackupModal');
  if(!btn||!modal)return;
  const info=document.getElementById('dataBackupInfo'), file=document.getElementById('restoreBackupFile');
  const close=()=>modal.classList.add('hidden');
  async function refresh(){try{const r=await fetch('/api/localdb/info',{cache:'no-store'}),j=await r.json();const kb=((j.bytes||0)/1024).toFixed(1);info.textContent=`SQLite දත්ත ගබඩාව • සුරැකි කොටස් ${j.records||0} • ${kb} KB`;}catch(e){info.textContent='දත්ත ගබඩාවේ තත්ත්වය ලබාගත නොහැකි විය.';}}
  btn.onclick=()=>{modal.classList.remove('hidden');refresh();};
  document.getElementById('dataBackupClose').onclick=close; modal.addEventListener('click',e=>{if(e.target===modal)close();});
  document.getElementById('downloadBackupBtn').onclick=async()=>{
    try{const r=await fetch('/api/localdb/state',{cache:'no-store'}),j=await r.json();const pack={format:'HelaJyotishyaBackup',version:'3.3',created_at:new Date().toISOString(),state:j.state||{}};const blob=new Blob([JSON.stringify(pack,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`Hela_Jyotishya_Backup_${new Date().toISOString().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000);}
    catch(e){alert('උපස්ථ ගොනුව සකස් කළ නොහැකි විය.');}
  };
  document.getElementById('restoreBackupBtn').onclick=()=>file.click();
  file.onchange=async()=>{
    const f=file.files&&file.files[0];if(!f)return;
    if(!confirm('මෙම උපස්ථ ගොනුවේ දත්තවලින් දැනට ඇති දත්ත ප්‍රතිස්ථාපනය කරන්නද?')){file.value='';return;}
    try{const pack=JSON.parse(await f.text());if(pack.format!=='HelaJyotishyaBackup'||!pack.state||typeof pack.state!=='object')throw new Error('bad');const r=await fetch('/api/localdb/restore',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:pack.state})});if(!r.ok)throw new Error('restore');Object.keys(localStorage).filter(k=>k.startsWith('hela_')||k==='jyotishya_settings').forEach(k=>localStorage.removeItem(k));Object.entries(pack.state).forEach(([k,v])=>localStorage.setItem(k,JSON.stringify(v)));alert('දත්ත සාර්ථකව ප්‍රතිස්ථාපනය කළා. මෘදුකාංගය නැවත පූරණය වේ.');location.reload();}
    catch(e){alert('මෙය වලංගු හෙළ ජ්‍යෝතිෂ්‍ය උපස්ථ ගොනුවක් නොවේ.');}finally{file.value='';}
  };
})();


// --- V4.0 Full Commercial Suite additions ---
(function(){
  const byId=(id)=>document.getElementById(id);
  const modalOpen=id=>byId(id)?.classList.remove('hidden');
  const modalClose=id=>byId(id)?.classList.add('hidden');
  function hookModal(btnId,modalId,closeId){const b=byId(btnId),m=byId(modalId),c=byId(closeId);if(!b||!m)return;b.onclick=()=>modalOpen(modalId);if(c)c.onclick=()=>modalClose(modalId);m.addEventListener('click',e=>{if(e.target===m)modalClose(modalId)});}

  // Accuracy center
  hookModal('accuracyBtn','accuracyModal','accuracyClose');
  const run=byId('accuracyRun'), out=byId('accuracyResults');
  if(run) run.onclick=async()=>{
    out.innerHTML='<div class="note">ගණිත ස්ථාවරත්වය පරීක්ෂා කරමින්...</div>';
    try{
      const r=await post('/api/accuracy',mainPayload());
      const ok=r.deterministic;
      out.innerHTML=`<div class="audit-hero ${ok?'audit-ok':'audit-bad'}"><b>${ok?'✓ එකම දත්ත = එකම ජන්ම ගණිත ප්‍රතිඵලය':'! ගණිත වෙනසක් හමු විය'}</b><span>Signature: ${esc(r.natal_signature||'—')}</span></div>
      <div class="audit-grid"><div><small>භාවිත කාල කලාපය</small><b>UTC ${r.timezone_used>=0?'+':''}${esc(r.timezone_used)}</b><span>${esc(r.timezone_source)}</span></div><div><small>UTC උපන් වේලාව</small><b>${esc(r.utc_datetime)}</b><span>JD ${esc(r.julian_day)}</span></div><div><small>අයනංශය</small><b>${esc(r.ayanamsa)}</b><span>${esc(r.node_mode)}</span></div><div><small>භාව ක්‍රමය</small><b>${esc(r.house_method)}</b><span>${esc(r.profile||'')}</span></div><div><small>ලග්නය</small><b>${esc(r.ascendant?.name)} ${Number(r.ascendant?.longitude||0).toFixed(6)}°</b><span>repeat Δ ${r.ascendant?.difference}</span></div><div><small>චන්ද්‍රයා</small><b>${esc(r.moon?.sign)}</b><span>${esc(r.moon?.nakshatra)} • පාදය ${r.moon?.pada}</span></div></div>
      <div class="subsection-title">ග්‍රහ ස්ඵුට නැවත-ගණනය සසඳීම</div><div class="audit-table">${(r.rows||[]).map(x=>`<div><b>${esc(x.planet)}</b><span>${Number(x.longitude).toFixed(6)}°</span><span>Δ ${x.difference}</span><strong>${x.same?'✓':'!'}</strong></div>`).join('')}</div><div class="note">${esc(r.warning||'')}</div>`;
    }catch(e){out.innerHTML=`<div class="note">${esc(e.message||'පරීක්ෂාව අසාර්ථකයි.')}</div>`}
  };
  if(byId('accuracyPrint')) byId('accuracyPrint').onclick=()=>printableWindow('ගණිත සත්‍යාපන වාර්තාව',out?.innerHTML||'','PHKS Creation • Hela Jyotishya V4.0');

  // Commercial license customer registry (management record; provider issues real keys)
  hookModal('licenseAdminBtn','licenseAdminModal','licenseAdminClose');
  const LS_LIC='hela_license_customers_v40';
  const loadLic=()=>{try{return JSON.parse(localStorage.getItem(LS_LIC)||'[]')}catch(e){return[]}};
  const saveLic=a=>{localStorage.setItem(LS_LIC,JSON.stringify(a));dbMirrorSet(LS_LIC,a)};
  function renderLic(){const el=byId('licenseAdminList');if(!el)return;const a=loadLic();el.innerHTML=a.length?a.map(x=>`<div class="record-row"><div><b>${esc(x.customer||'නම නොමැත')} • ${esc(x.plan)}</b><span>${esc(x.status)} • ${esc(x.start||'')} ${x.end?'→ '+esc(x.end):''}<br>${esc(x.key||'')} ${x.device?'• '+esc(x.device):''}</span></div><div class="record-actions"><button data-lic-del="${x.id}">මකන්න</button></div></div>`).join(''):'<div class="note">බලපත්‍ර ගනුදෙනුකරුවන් තව සුරැකී නැත.</div>';el.querySelectorAll('[data-lic-del]').forEach(b=>b.onclick=()=>{saveLic(loadLic().filter(x=>x.id!==b.dataset.licDel));renderLic()});}
  byId('licenseAdminBtn')?.addEventListener('click',renderLic);
  if(byId('licStart')&&!byId('licStart').value)byId('licStart').value=new Date().toISOString().slice(0,10);
  if(byId('licSave'))byId('licSave').onclick=()=>{const x={id:String(Date.now()),customer:byId('licCustomer').value.trim(),phone:byId('licPhone').value.trim(),plan:byId('licPlan').value,key:byId('licKeyRef').value.trim(),start:byId('licStart').value,end:byId('licEnd').value,status:byId('licStatus').value,device:byId('licDevice').value.trim()};const a=loadLic();a.unshift(x);saveLic(a);renderLic()};
  if(byId('licWhatsApp'))byId('licWhatsApp').onclick=()=>window.open('https://wa.me/94715954563','_blank');

  // Update center
  hookModal('updateCenterBtn','updateCenterModal','updateCenterClose');
  if(byId('updateCheckBtn'))byId('updateCheckBtn').onclick=async()=>{const info=byId('updateCenterInfo');info.textContent='පරීක්ෂා කරමින්...';try{const r=await fetch('/api/update/check',{cache:'no-store'}),j=await r.json();if(!j.configured){info.innerHTML=`<b>දැනට භාවිතය:</b> ${esc(j.current||'V4.0')}<br>${esc(j.message||'Release manifest URL එක Settings/Config තුළ සකසන්න.')}`;}else if(j.ok){info.innerHTML=`<b>දැනට:</b> ${esc(j.current)}<br><b>නවතම:</b> ${esc(j.latest||'—')}<br>${esc(j.notes||'')}${j.download_url?`<br><a href="${esc(j.download_url)}" target="_blank">යාවත්කාලීන ගොනුව විවෘත කරන්න</a>`:''}`;}else info.textContent='යාවත්කාලීන පරීක්ෂාව අසාර්ථකයි: '+(j.message||'');}catch(e){info.textContent='යාවත්කාලීන පරීක්ෂාව අසාර්ථකයි.'}};
  if(byId('updateSupportBtn'))byId('updateSupportBtn').onclick=()=>window.open('https://wa.me/94715954563','_blank');

  // Extend backup center with integrity / optimization button
  const acts=byId('dataBackupModal')?.querySelector('.settings-actions');
  if(acts&&!byId('dbIntegrityBtn')){const b=document.createElement('button');b.id='dbIntegrityBtn';b.className='outline-btn';b.textContent='දත්ත ගබඩාව පරීක්ෂා / Optimize';acts.appendChild(b);b.onclick=async()=>{const info=byId('dataBackupInfo');try{const r=await fetch('/api/localdb/integrity',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({repair:true})}),j=await r.json();info.textContent=j.ok?`SQLite Integrity: OK • කොටස් ${j.records} • Optimize සම්පූර්ණයි`:`SQLite Integrity: ${j.result}`;}catch(e){info.textContent='SQLite පරීක්ෂාව අසාර්ථකයි.'}}}
})();

const projects=[{"slug":"land-use-dynamics","title":"Multi-sector land-use dynamics","tag":"Python · Land-Use Change · GIS","img":"figure-02-msd-classes.png","alt":"Original MSD land-cover classification map","description":"U.S. land-cover classification and harmonization","repo":"https://github.com/jayjayanton/oliver-mcmanamay_2025_scidata","label":"Research scripts"},{"slug":"colombia-deforestation","title":"Colombia deforestation","tag":"Python · R · Deforestation Modeling","img":"colombia-deforestation-risk.jpg","alt":"Colombia modeled deforestation-risk map","description":"Deforestation modeling and geographic drivers","repo":"https://github.com/jayjayanton/Deforestation-Research","label":"View R scripts"},{"slug":"orphaned-wells","title":"Orphaned wells","tag":"Python · XGBoost · Classification","img":"Appalachian%20Basin%20Well%20Classification%20Map.png","alt":"Illustrative map of Appalachian Basin wells with synthetic orphaned-well probabilities","description":"Geospatial XGBoost classification and model interpretation","repo":"https://github.com/jayjayanton/Orphaned-Wells-","label":"View research code"},{"slug":"traffic-camera-pipeline","title":"Traffic camera extraction","tag":"Python · OpenCV · Automated Extraction","img":"1.jpg","alt":"Actual City of Austin traffic camera snapshot from November 2026","description":"Texas roadway snapshots and Jackson Hole video frames","repo":"https://github.com/jayjayanton/Webcam-Data-Extraction","label":"View Python scripts"},{"slug":"carbon-storage-atlas","title":"Carbon storage atlas","tag":"Python · Automation · Raster-to-Vector · ArcGIS","img":"Carbon_Storage_Image.png","alt":"Illustrative geospatial raster processing workflow","description":"Automated conversion of 400+ geologic rasters to GIS-ready vector layers","repo":null,"label":"Proprietary analysis"},{"slug":"coal-ash-modeling","title":"Coal ash modeling","tag":"Python · XGBoost · Regression","img":"Coal_Ash_Concept.png","alt":"Conceptual cover art showing coal ash deposits and varied mineral constituents","description":"Predictive modeling of coal ash chemistry","repo":null,"label":"Proprietary analysis"},{"slug":"epa-emissions","title":"EPA emissions automation","tag":"Python · ETL Automation · Data Standardization","img":"placeholder-data.svg","alt":"Illustrative data engineering workflow","description":"Greenhouse gas data extraction and standardization","repo":null,"label":"Proprietary analysis"},{"slug":"nasa-air-quality","title":"NASA · Air Quality & Public Health","tag":"Python · ArcGIS · R · Linear Regression","img":"nasa-air-quality-cover.png","alt":"Stylized aerosol optical depth visualization of Central America","description":"El Salvador: satellite AOD, in-situ observations and PM2.5 analysis","repo":"https://github.com/jayjayanton/NASA-Projects/tree/main/air-quality-el-salvador","label":"NASA project repository"},{"slug":"nasa-water-resources","title":"NASA · Water Resources & Mesquite Forest Change","tag":"Python · ArcGIS · Time Series · Automation","img":"nasa-water-resources-cover.png","alt":"Stylized NDVI-inspired vegetation visualization of northern Peru","description":"Lambayeque, Peru: NDVI, precipitation and soil-moisture time series","repo":"https://github.com/jayjayanton/NASA-Projects/tree/main/water-resources-lambayeque","label":"NASA project repository"},{"slug":"raaz-borg","title":"Ra'az Borg — Web Development","tag":"HTML · CSS · JavaScript · UI/UX","img":"https://raw.githubusercontent.com/jayjayanton/raaz-borg/main/assets/squad-magenta.jpg","alt":"Ra'az Borg combat-sports website visual asset","description":"Responsive bilingual combat-sports website with interactive frontend features","repo":"https://github.com/jayjayanton/raaz-borg","label":"View GitHub fork"},{"slug":"environmental-flows","title":"Texas Environmental Flows","tag":"R · Python · Watersheds · ML","img":"https://raw.githubusercontent.com/jayjayanton/Texas-Environmental-Flows-ML/main/figures/all_ecoregions_comparison.png","alt":"Texas ecoregion HIT metric mean R squared model-fit curves","description":"Watershed delineation, stream classification, and hydrologic alteration analysis","repo":"https://github.com/jayjayanton/Texas-Environmental-Flows-ML","label":"Research scripts"}];
(function(){
  const track=document.getElementById("projects-grid");
  const viewport=document.getElementById("project-carousel-viewport");
  const panel=document.getElementById("projects-reveal");
  const controls=document.getElementById("project-carousel-controls");
  const prev=document.getElementById("project-prev");
  const next=document.getElementById("project-next");
  const counter=document.getElementById("project-counter");
  const buttons=[...document.querySelectorAll("[data-project-tab]")];
  const status=document.getElementById("project-discipline-description");
  if(!track||!viewport||!panel||!controls||!prev||!next||!counter)return;
  const groups={data:projects.filter(p=>p.slug!=="raaz-borg"),web:projects.filter(p=>p.slug==="raaz-borg")};
  let selected=null,index=0,startX=null;
  const stateKey="portfolio-projects-position";
  function savePosition(){
    try { sessionStorage.setItem(stateKey,JSON.stringify({category:selected,index,scrollY:window.scrollY})); } catch(e) {}
  }
  window.addEventListener("pagehide",savePosition);
  function card(p,i,n){
    const src=p.img.startsWith("https://")?p.img:"images/"+p.img;
    return `<article class="project-card project-carousel__slide" role="group" aria-roledescription="slide" aria-label="${i+1} of ${n}: ${p.title}"><a class="project-card__image" href="projects/${p.slug}.html"><img src="${src}" alt="${p.alt}" loading="lazy"></a><div class="project-card__body"><p class="eyebrow">${p.tag}</p><h3><a href="projects/${p.slug}.html">${p.title}</a></h3><p>${p.description}</p><div class="project-card__links"><a href="projects/${p.slug}.html">View case study</a>${p.repo?`<a href="${p.repo}" target="_blank" rel="noopener noreferrer">View code</a>`:"<span class='muted'>Code not public</span>"}</div></div></article>`;
  }
  function go(to){
    if(!selected)return;
    const n=groups[selected].length;
    index=Math.max(0,Math.min(to,n-1));
    track.style.transform=`translate3d(-${index*100}%,0,0)`;
    counter.textContent=`${index+1} / ${n}`;
    prev.disabled=index===0;
    next.disabled=index===n-1;
    savePosition();
  }
  function select(cat){
    selected=cat;
    buttons.forEach(b=>{
      const active=b.dataset.projectTab===cat;
      b.setAttribute("aria-expanded",String(active));
      b.setAttribute("aria-pressed",String(active));
    });
    if(status)status.textContent=!cat?"Choose a category to view its projects.":cat==="web"?"Web development projects":"Data science, geospatial research and automation projects";
    if(!cat){
      panel.classList.remove("is-open");
      panel.inert=true;
      panel.setAttribute("aria-hidden","true");
      savePosition();
      return;
    }
    const items=groups[cat];
    track.innerHTML=items.map((p,i)=>card(p,i,items.length)).join("");
    track.style.transition="none";
    track.style.transform="translate3d(0,0,0)";
    index=0;
    controls.hidden=items.length<2;
    go(0);
    requestAnimationFrame(()=>{track.style.transition="";});
    panel.inert=false;
    panel.setAttribute("aria-hidden","false");
    panel.classList.add("is-open");
    savePosition();
  }
  buttons.forEach(b=>b.addEventListener("click",()=>select(selected===b.dataset.projectTab?null:b.dataset.projectTab)));
  prev.addEventListener("click",()=>go(index-1));
  next.addEventListener("click",()=>go(index+1));
  viewport.addEventListener("touchstart",e=>{startX=e.touches[0].clientX;},{passive:true});
  viewport.addEventListener("touchend",e=>{
    if(startX===null||!selected)return;
    const delta=e.changedTouches[0].clientX-startX;
    startX=null;
    if(Math.abs(delta)>45)go(index+(delta<0?1:-1));
  },{passive:true});
  viewport.addEventListener("keydown",e=>{
    if(e.key==="ArrowRight"||e.key==="ArrowLeft"){e.preventDefault();go(index+(e.key==="ArrowRight"?1:-1));}
  });
  panel.inert=true;
  let saved=null;
  try { saved=JSON.parse(sessionStorage.getItem(stateKey)||"null"); } catch(e) {}
  if(saved && (saved.category==="data" || saved.category==="web")){
    select(saved.category);
    go(Number.isInteger(saved.index)?saved.index:0);
    requestAnimationFrame(()=>window.scrollTo(0,Math.max(0,Number(saved.scrollY)||0)));
  } else {
    select(null);
  }
  document.querySelectorAll("[data-year]").forEach(el=>el.textContent=new Date().getFullYear());
})();
const projects=[{"slug":"land-use-dynamics","title":"Multi-sector land-use dynamics","tag":"Python · Land-Use Change · GIS","img":"figure-02-msd-classes.png","alt":"Original MSD land-cover classification map","description":"U.S. land-cover classification and harmonization","repo":"https://github.com/jayjayanton/oliver-mcmanamay_2025_scidata","label":"Research scripts"},{"slug":"colombia-deforestation","title":"Colombia deforestation","tag":"Python · R · Deforestation Modeling","img":"colombia-deforestation-risk.jpg","alt":"Colombia modeled deforestation-risk map","description":"Deforestation modeling and geographic drivers","repo":"https://github.com/jayjayanton/Deforestation-Research","label":"View R scripts"},{"slug":"orphaned-wells","title":"Orphaned wells","tag":"Python · XGBoost · Classification","img":"Appalachian%20Basin%20Well%20Classification%20Map.png","alt":"Illustrative map of Appalachian Basin wells with synthetic orphaned-well probabilities","description":"Geospatial XGBoost classification and model interpretation","repo":"https://github.com/jayjayanton/Orphaned-Wells-","label":"View research code"},{"slug":"traffic-camera-pipeline","title":"Traffic camera extraction","tag":"Python · OpenCV · Automated Extraction","img":"placeholder-webcam.svg","alt":"Illustrative webcam data extraction workflow","description":"Texas roadway snapshots and Jackson Hole video frames","repo":"https://github.com/jayjayanton/Webcam-Data-Extraction","label":"View Python scripts"},{"slug":"carbon-storage-atlas","title":"Carbon storage atlas","tag":"Python · Raster ETL · ArcGIS Pro","img":"placeholder-geospatial.svg","alt":"Illustrative geospatial raster processing workflow","description":"Geologic raster processing and map publication","repo":null,"label":"Proprietary analysis"},{"slug":"coal-ash-modeling","title":"Coal ash modeling","tag":"Python · XGBoost · Regression","img":"placeholder-modeling.svg","alt":"Illustrative modeling workflow","description":"Predictive modeling of coal ash chemistry","repo":null,"label":"Proprietary analysis"},{"slug":"epa-emissions","title":"EPA emissions automation","tag":"Python · ETL Automation · Data Standardization","img":"placeholder-data.svg","alt":"Illustrative data engineering workflow","description":"Greenhouse gas data extraction and standardization","repo":null,"label":"Proprietary analysis"},{"slug":"nasa-air-quality","title":"NASA · Air Quality & Public Health","tag":"Python · ArcGIS · R · Linear Regression","img":"nasa-air-quality-cover.png","alt":"Stylized aerosol optical depth visualization of Central America","description":"El Salvador: satellite AOD, in-situ observations and PM2.5 analysis","repo":"https://github.com/jayjayanton/NASA-Projects/tree/main/air-quality-el-salvador","label":"NASA project repository"},{"slug":"nasa-water-resources","title":"NASA · Water Resources & Mesquite Forest Change","tag":"Python · ArcGIS · Time Series · Automation","img":"nasa-water-resources-cover.png","alt":"Stylized NDVI-inspired vegetation visualization of northern Peru","description":"Lambayeque, Peru: NDVI, precipitation and soil-moisture time series","repo":"https://github.com/jayjayanton/NASA-Projects/tree/main/water-resources-lambayeque","label":"NASA project repository"},{"slug":"raaz-borg","title":"Ra'az Borg — Web Development","tag":"HTML · CSS · JavaScript · UI/UX","img":"https://raw.githubusercontent.com/jayjayanton/raaz-borg/main/assets/squad-magenta.jpg","alt":"Ra'az Borg combat-sports website visual asset","description":"Responsive bilingual combat-sports website with interactive frontend features","repo":"https://github.com/jayjayanton/raaz-borg","label":"View GitHub fork"},{"slug":"environmental-flows","title":"Texas Environmental Flows","tag":"R · Python · Watersheds · ML","img":"https://raw.githubusercontent.com/jayjayanton/Texas-Environmental-Flows-ML/main/figures/all_ecoregions_comparison.png","alt":"Texas ecoregion HIT metric mean R squared model-fit curves","description":"Watershed delineation, stream classification, and hydrologic alteration analysis","repo":"https://github.com/jayjayanton/Texas-Environmental-Flows-ML","label":"Research scripts"}];
(function(){
  const viewport=document.getElementById("projects-grid");
  const panel=document.getElementById("projects-reveal");
  const controls=document.getElementById("project-carousel-controls");
  const prev=document.getElementById("project-prev");
  const next=document.getElementById("project-next");
  const counter=document.getElementById("project-counter");
  const buttons=[...document.querySelectorAll("[data-project-tab]")];
  const status=document.getElementById("project-discipline-description");
  if(!viewport||!panel||!controls||buttons.length!==2)return;
  const reduced=window.matchMedia("(prefers-reduced-motion: reduce)");
  const groups={data:projects.filter(p=>p.slug!=="raaz-borg"),web:projects.filter(p=>p.slug==="raaz-borg")};
  let selected=null,index=0,scrollFrame=0;
  const card=(p,i,total)=>{
    const src=p.img.startsWith("https://")?p.img:"images/"+p.img;
    return `<article class="project-card project-carousel__slide" role="group" aria-roledescription="slide" aria-label="${i+1} of ${total}: ${p.title}"><a class="project-card__image" href="projects/${p.slug}.html"><img src="${src}" alt="${p.alt}" loading="lazy"></a><div class="project-card__body"><p class="eyebrow">${p.tag}</p><h3><a href="projects/${p.slug}.html">${p.title}</a></h3><p>${p.description}</p><div class="project-card__links"><a href="projects/${p.slug}.html">View case study</a>${p.repo?`<a href="${p.repo}" target="_blank" rel="noopener noreferrer">${p.label}</a>`:"<span class='muted'>Code not public</span>"}</div></div></article>`;
  };
  function updateCounter(){
    const total=selected?groups[selected].length:0;
    counter.textContent=total?`${index+1} / ${total}`:"";
    prev.disabled=total<2||index===0;
    next.disabled=total<2||index===total-1;
  }
  function go(i){
    if(!selected)return;
    index=Math.max(0,Math.min(i,groups[selected].length-1));
    const slide=viewport.children[index];
    if(slide)viewport.scrollTo({left:slide.offsetLeft-viewport.children[0].offsetLeft,behavior:reduced.matches?"instant":"smooth"});
    updateCounter();
  }
  function renderButtons(){
    buttons.forEach(b=>{
      const active=b.dataset.projectTab===selected;
      b.setAttribute("aria-expanded",String(active));
      b.setAttribute("aria-pressed",String(active));
    });
    if(status)status.textContent=selected===null?"Choose a category to view its projects.":selected==="web"?"Web development projects":"Data science, geospatial research and automation projects";
  }
  function select(nextCategory){
    selected=nextCategory;
    index=0;
    renderButtons();
    if(!selected){
      panel.classList.remove("is-open");
      panel.setAttribute("aria-hidden","true");
      panel.inert=true;
      return;
    }
    const items=groups[selected];
    viewport.innerHTML=items.map((p,i)=>card(p,i,items.length)).join("");
    viewport.scrollLeft=0;
    controls.hidden=items.length<2;
    updateCounter();
    panel.inert=false;
    panel.setAttribute("aria-hidden","false");
    panel.classList.add("is-open");
  }
  buttons.forEach(b=>b.addEventListener("click",()=>select(selected===b.dataset.projectTab?null:b.dataset.projectTab)));
  prev.addEventListener("click",()=>go(index-1));
  next.addEventListener("click",()=>go(index+1));
  viewport.addEventListener("scroll",()=>{
    if(scrollFrame)cancelAnimationFrame(scrollFrame);
    scrollFrame=requestAnimationFrame(()=>{
      if(!selected||!viewport.children.length)return;
      const width=viewport.clientWidth;
      index=Math.max(0,Math.min(groups[selected].length-1,Math.round(viewport.scrollLeft/Math.max(width,1))));
      updateCounter();
    });
  },{passive:true});
  viewport.addEventListener("keydown",e=>{
    if(e.target.closest("a,button"))return;
    if(e.key==="ArrowRight"||e.key==="ArrowLeft"){e.preventDefault();go(index+(e.key==="ArrowRight"?1:-1));}
  });
  panel.inert=true;
  renderButtons();
  document.querySelectorAll("[data-year]").forEach(el=>el.textContent=new Date().getFullYear());
})();
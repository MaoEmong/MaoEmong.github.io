const search=document.querySelector('#project-search');
const filters=[...document.querySelectorAll('[data-filter]')];
const rows=[...document.querySelectorAll('[data-project]')];
let category='전체';
function filterProjects(){
 if(!search)return;
 const query=search.value.trim().toLocaleLowerCase();let count=0;
 for(const row of rows){const matches=(category==='전체'||row.dataset.category===category)&&row.dataset.search.includes(query);row.hidden=!matches;if(matches)count++;}
 for(const button of filters)button.setAttribute('aria-pressed',String(button.dataset.filter===category));
 document.querySelector('#result-count').textContent=`${category==='전체'?'전체':category} ${count}개`;
 document.querySelector('.empty-state').hidden=count!==0;
 const params=new URLSearchParams();if(query)params.set('q',search.value.trim());if(category!=='전체')params.set('category',category);
 history.replaceState(null,'',location.pathname+(params.size?'?'+params:'')+location.hash);
}
if(search){const params=new URLSearchParams(location.search);search.value=(params.get('q')||'').slice(0,100);const requested=params.get('category');if(filters.some(b=>b.dataset.filter===requested))category=requested;search.addEventListener('input',filterProjects);for(const button of filters)button.addEventListener('click',()=>{category=button.dataset.filter;filterProjects();});document.querySelector('#reset-search').addEventListener('click',()=>{search.value='';category='전체';filterProjects();search.focus();});filterProjects();}
let toastTimer;function toast(message){const node=document.querySelector('.toast');node.textContent=message;node.classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>node.classList.remove('visible'),2700);}
document.querySelector('.copy-link')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);toast('페이지 주소를 복사했습니다.');}catch{toast('브라우저 주소창의 주소를 복사해 주세요.');}});
const dialog=document.querySelector('.image-dialog');let lastImageButton;
for(const button of document.querySelectorAll('[data-image]'))button.addEventListener('click',()=>{lastImageButton=button;dialog.querySelector('img').src=button.dataset.image;dialog.querySelector('img').alt=button.dataset.caption;dialog.querySelector('p').textContent=button.dataset.caption;dialog.showModal();});
dialog?.addEventListener('close',()=>lastImageButton?.focus());
dialog?.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
document.addEventListener('keydown',event=>{if(event.key==='Escape')document.querySelector('.mobile-menu')?.removeAttribute('open');});
// Measure list descriptions after fonts load; native HTML remains usable without JS.
import {prepare,layout} from './vendor/pretext/layout.js';
await document.fonts.ready;
const descriptions=[...document.querySelectorAll('[data-pretext]')];const prepared=new Map();
function measure(){for(const element of descriptions){if(element.closest('[hidden]'))continue;const style=getComputedStyle(element);const font=`${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;let item=prepared.get(element);if(!item||item.font!==font){item={font,handle:prepare(element.textContent,font)};prepared.set(element,item);}const result=layout(item.handle,element.clientWidth,parseFloat(style.lineHeight));element.style.minHeight=`${result.height}px`;}}
if(descriptions.length){let frame;new ResizeObserver(()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(measure);}).observe(document.querySelector('.project-list'));measure();for(const button of filters)button.addEventListener('click',()=>requestAnimationFrame(measure));search?.addEventListener('input',()=>requestAnimationFrame(measure));}

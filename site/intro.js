/* QAYO İNŞAAT — sayt giriş videosu: video oynayır, bitəndə kataloq açılır.
   DEFAULT_ON=false: yalnız ?qayo_video=1 ilə görünür (yoxlama rejimi).
   Canlıya qoyulanda DEFAULT_ON=true edilir; ?qayo_intro=0 videonu keçir. */
(function(){
"use strict";
var DEFAULT_ON=false;
var VIDEO="/qayo-intro-video/qayo-insaat-azerbaycan-web.mp4";
var POSTER="/qayo-intro-video/poster.jpg";
var path=location.pathname.replace(/\/+$/,"")||"/";
if(path!=="/onlayn-satis"&&path!=="/")return;
var q=new URLSearchParams(location.search);
if(q.get("qayo_intro")==="0"||q.get("qayo_video")==="0")return;
if(!(DEFAULT_ON||q.get("qayo_video")==="1"))return;
if(document.getElementById("qayo-intro-video"))return;
var st=document.createElement("style");
st.textContent="#qayo-intro-video{position:fixed;inset:0;z-index:2147483000;background:#00152e;display:flex;align-items:center;justify-content:center;opacity:1;transition:opacity .5s ease}#qayo-intro-video.qiv-out{opacity:0;pointer-events:none}#qayo-intro-video video{width:100%;height:100%;object-fit:contain;background:#00152e}#qayo-intro-video button{position:absolute;border:0;border-radius:22px;padding:10px 16px;min-height:44px;font:800 14px/1 Arial,sans-serif;color:#fff;background:rgba(0,21,46,.72);border:1px solid rgba(255,255,255,.55);cursor:pointer}#qayo-intro-video .qiv-skip{top:max(12px,env(safe-area-inset-top));right:12px}#qayo-intro-video .qiv-sound{left:12px;bottom:max(18px,env(safe-area-inset-bottom))}#qayo-intro-video button:focus-visible{outline:3px solid #f7c532;outline-offset:2px}";
document.head.appendChild(st);
var catalog=document.querySelector("main.catalog");
var prevInert=catalog?catalog.inert:false;
var prevOverflow=document.body.style.overflow;
var ov=document.createElement("section");
ov.id="qayo-intro-video";
ov.setAttribute("role","dialog");ov.setAttribute("aria-modal","true");
ov.setAttribute("aria-label","QAYO İNŞAAT giriş videosu");
ov.innerHTML='<video playsinline webkit-playsinline muted preload="auto" poster="'+POSTER+'" aria-label="QAYO İNŞAAT Azərbaycan"><source src="'+VIDEO+'" type="video/mp4"></video><button type="button" class="qiv-skip">KEÇ ↗</button><button type="button" class="qiv-sound">🔊 SƏSLİ İZLƏ</button>';
var v=ov.querySelector("video"),done=false,started=false;
function finish(){
 if(done)return;done=true;
 try{v.pause()}catch(_){}
 ov.classList.add("qiv-out");
 document.body.style.overflow=prevOverflow;
 if(catalog)catalog.inert=prevInert;
 try{window.scrollTo(0,0)}catch(_){}
 setTimeout(function(){ov.remove();st.remove()},600);
}
document.body.appendChild(ov);
document.body.style.overflow="hidden";
if(catalog)catalog.inert=true;
ov.querySelector(".qiv-skip").addEventListener("click",finish);
var sound=ov.querySelector(".qiv-sound");
sound.addEventListener("click",function(){
 v.muted=!v.muted;
 sound.textContent=v.muted?"🔊 SƏSLİ İZLƏ":"🔇 SƏSSİZ";
 if(v.paused)try{v.play()}catch(_){}
});
document.addEventListener("keydown",function esc(e){if(e.key==="Escape"){finish();document.removeEventListener("keydown",esc)}});
v.addEventListener("ended",finish);
v.addEventListener("playing",function(){started=true});
v.addEventListener("error",finish);
v.addEventListener("stalled",function(){setTimeout(function(){if(!started)finish()},4000)});
try{var p=v.play();if(p&&p.catch)p.catch(function(){setTimeout(function(){if(!started)finish()},3000)})}catch(_){finish()}
setTimeout(function(){if(!started)finish()},9000);
setTimeout(finish,32000);
})();

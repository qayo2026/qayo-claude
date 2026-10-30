/* QAYO İNŞAAT — sayt giriş videosu (təcrid olunmuş konteyner).
   Video ayrıca səhifədə (/qayo-intro-video/player.html) iframe-də işləyir:
   kataloqun yazı/CSS/JS dəyişiklikləri videoya təsir etmir, video da kataloqa.
   DEFAULT_ON=true: hamı üçün canlıdır (30.10.2026).
   Canlıya qoyulanda DEFAULT_ON=true; ?qayo_intro=0 videonu keçir. */
(function(){
"use strict";
var DEFAULT_ON=true;
var path=location.pathname.replace(/\/+$/,"")||"/";
if(path!=="/onlayn-satis"&&path!=="/")return;
var q=new URLSearchParams(location.search);
if(q.get("qayo_intro")==="0"||q.get("qayo_video")==="0")return;
if(!(DEFAULT_ON||q.get("qayo_video")==="1"))return;
if(document.getElementById("qayo-intro-frame"))return;
var catalog=document.querySelector("main.catalog");
var prevInert=catalog?catalog.inert:false,prevOverflow=document.body.style.overflow;
var fr=document.createElement("iframe");
fr.id="qayo-intro-frame";fr.title="QAYO İNŞAAT giriş videosu";fr.setAttribute("allow","autoplay");
fr.src="/qayo-intro-video/player.html?v=7";
fr.style.cssText="position:fixed;inset:0;width:100%;height:100%;border:0;z-index:2147483000;background:#00152e;opacity:1;transition:opacity .5s ease";
var done=false,started=false,ready=false,long=0;
function finish(){
 if(done)return;done=true;
 window.removeEventListener("message",onMsg);
 fr.style.opacity="0";fr.style.pointerEvents="none";
 document.body.style.overflow=prevOverflow;
 if(catalog)catalog.inert=prevInert;
 try{window.scrollTo(0,0)}catch(_){}
 setTimeout(function(){fr.remove()},600);
}
function onMsg(e){
 if(e.origin!==location.origin||e.source!==fr.contentWindow||!e.data)return;
 if(e.data.qayoIntro==="ready")ready=true;
 if(e.data.qayoIntro==="started"){started=true;clearTimeout(long);long=setTimeout(finish,40000)}
 if(e.data.qayoIntro==="done")finish();
}
window.addEventListener("message",onMsg);
document.body.appendChild(fr);
document.body.style.overflow="hidden";
if(catalog)catalog.inert=true;
/* iframe yüklənməsə keç; yüklənibsə müştərinin ilk toxunuşunu gözlə (səs üçün) */
setTimeout(function(){if(!ready)finish()},9000);
long=setTimeout(finish,180000);
})();

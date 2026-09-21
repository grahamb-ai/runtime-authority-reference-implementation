const scenarios={
allow:{title:"Current standing ACTIVE",text:"Positive control: exact typed ACTIVE is required at the protected commit path.",standing:"ACTIVE",now:"ACTIVE",reader:"ACTIVE"},
withdrawn:{title:"Standing changes before consequence",text:"T0 was VALID/ACTIVE. Before consequence formation the synthetic condition changes to WITHDRAWN rev 2, so current standing is PREVENTED.",standing:"PREVENTED",now:"PREVENTED",reader:"PREVENTED"},
stale:{title:"Earlier capability after standing change",text:"An exact capability was issued at T0. Current standing then becomes PREVENTED. The protected gateway must not treat the earlier capability as sufficient.",standing:"PREVENTED",now:"PREVENTED",reader:"PREVENTED"},
dependency:{title:"Standing dependency robustness",text:"AIRP-009 challenges the standing reader itself. Only exact typed ACTIVE may permit the represented commit.",standing:"select below",now:"—",reader:"PREVENTED"}
};
let current="allow";
const controls=document.querySelector("#controls");
function dependencyControls(){
 controls.innerHTML='<label>Standing reader result <select id="reader"><option value="ACTIVE">exact typed ACTIVE</option><option value="PREVENTED">PREVENTED</option><option value="INDETERMINATE">INDETERMINATE</option><option value="NONE">unavailable / null</option><option value="STRING">plain string "ACTIVE"</option><option value="ERROR">reader exception</option><option value="MISSING">no standing reader</option></select></label>';
 document.querySelector("#reader").onchange=e=>{scenarios.dependency.reader=e.target.value; document.querySelector("#nowCard").textContent=e.target.options[e.target.selectedIndex].text;};
}
function render(){
 const s=scenarios[current]; document.querySelector("#scenarioTitle").textContent=s.title;document.querySelector("#scenarioText").textContent=s.text;
 document.querySelector("#standing").textContent=s.standing;document.querySelector("#nowCard").textContent=s.now;
 document.querySelector("#t0").textContent=current==="allow"?"VALID · rev 1":"VALID rev 1 → WITHDRAWN rev 2";
 document.querySelector("#eprState").textContent="waiting";document.querySelector("#epr").classList.remove("committed","blocked");
 document.querySelector("#result").className="result neutral";document.querySelector("#result").innerHTML="<strong>READY</strong><span>Attempt the represented commit.</span>";
 controls.innerHTML=current==="dependency"?"":'<span class="hint">'+(current==="stale"?"T0 capability retained · direct protected-gateway invocation":"Current standing is read at consequence time")+"</span>";
 if(current==="dependency")dependencyControls();
 document.querySelector("#trace").innerHTML="";
}
function outcome(){
 const s=scenarios[current];let r=s.reader;
 if(current==="dependency")r=document.querySelector("#reader").value;
 const committed=r==="ACTIVE";
 const reason=committed?"Exact typed current standing ACTIVE; represented protected path accepted.":r==="PREVENTED"?"Current standing PREVENTED; protected path failed closed.":r==="STRING"?"Plain string ACTIVE rejected; exact enum type required.":r==="MISSING"?"Standing reader absent; protected path failed closed.":r==="ERROR"?"Standing reader exception; protected path failed closed.":"Current standing cannot be established as exact typed ACTIVE; protected path failed closed.";
 document.querySelector("#eprState").textContent=committed?"COMMITTED":"UNCHANGED";
 document.querySelector("#epr").classList.add(committed?"committed":"blocked");
 document.querySelector("#result").className="result "+(committed?"ok":"stop");
 document.querySelector("#result").innerHTML="<strong>"+(committed?"COMMITTED":"BLOCKED")+"</strong><span>"+reason+"</span>";
 document.querySelector("#trace").innerHTML=[
 ["T0","VALID → ACTIVE"],
 ["Capability","attempt-A · exact payload"],
 ["Consequence-time standing",r],
 ["Gateway",committed?"COMMITTED":"BLOCKED"],
 ["Represented sink",committed?"1 synthetic note":"empty / unchanged"]
 ].map(x=>'<div><span>'+x[0]+'</span><b>'+x[1]+'</b></div>').join("");
}
document.querySelectorAll("[data-s]").forEach(b=>b.onclick=()=>{document.querySelectorAll("[data-s]").forEach(x=>x.classList.remove("active"));b.classList.add("active");current=b.dataset.s;render();});
document.querySelector("#execute").onclick=outcome;render();
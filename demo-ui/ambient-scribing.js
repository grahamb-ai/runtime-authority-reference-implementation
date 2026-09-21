const scenarios={
 unchanged:{title:"Nothing relevant changes",text:"Positive control. The earlier conditions remain current when the represented commit is attempted.",t0:"VALID · rev 1",note:"synthetic-note-A",change:"No relevant change",detail:"conditions remain current",standing:"ACTIVE",match:"MATCH",reader:"ACTIVE"},
 dissent:{title:"A relevant condition changes before commitment",text:"Synthetic example grounded in an ordinary workflow event: after the earlier valid state, the patient position changes before the represented EPR commit.",t0:"VALID · rev 1",note:"synthetic-note-A",change:"Patient dissents",detail:"new evidence · rev 2",standing:"PREVENTED",match:"MATCH",reader:"PREVENTED"},
 payload:{title:"The approved object is no longer the object presented",text:"Draft A was the earlier represented object. Before commitment, the proposed payload becomes Draft B. FlowSignal asks whether what is about to happen still matches what was authorised.",t0:"VALID · rev 1",note:"approved draft A",change:"Payload changed",detail:"draft A → draft B",standing:"ACTIVE",match:"NO MATCH",reader:"ACTIVE"},
 dependency:{title:"Can current standing be established?",text:"This scenario challenges the standing dependency itself. It does not assert that the underlying clinical state changed. Only an exact typed ACTIVE result permits the represented protected path.",t0:"VALID · rev 1",note:"synthetic-note-A",change:"Standing source under test",detail:"reader response below",standing:"select below",match:"MATCH",reader:"ACTIVE"}
};
let current="unchanged",withFlow=true;
const $=s=>document.querySelector(s), controls=$("#controls");
function dependencyControls(){
 controls.innerHTML='<label>Standing reader result <select id="reader"><option value="ACTIVE">exact typed ACTIVE</option><option value="PREVENTED">PREVENTED</option><option value="INDETERMINATE">INDETERMINATE</option><option value="NONE">unavailable / null</option><option value="STRING">plain string "ACTIVE"</option><option value="ERROR">reader exception</option><option value="MISSING">no standing reader</option></select></label>';
 $("#reader").onchange=e=>{$("#nowCard").textContent=e.target.options[e.target.selectedIndex].text;};
}
function render(){
 const s=scenarios[current];
 $("#scenarioTitle").textContent=s.title; $("#scenarioText").textContent=s.text;
 $("#t0State").textContent=s.t0; $("#noteState").textContent=s.note; $("#changeTitle").textContent=s.change; $("#changeDetail").textContent=s.detail;
 $("#changeBox").classList.toggle("changed",current!=="unchanged");
 $("#modePill").textContent=withFlow?"WITH FLOWSIGNAL":"WITHOUT FLOWSIGNAL";
 $("#modePill").className="mode-pill "+(withFlow?"with":"without");
 $("#gateSmall").textContent=withFlow?"T1 · B4 ACT":"COMPARATOR PATH";
 $("#gateTitle").textContent=withFlow?"Consequence-time authority check":"No consequence-time authority check";
 $("#gateState").textContent=withFlow?(current==="dependency"?"standing dependency evaluated":"WHO · WHAT · NOW · MATCH"):"earlier state relied upon";
 $("#gateNode").classList.toggle("gate-off",!withFlow);
 $("#nowCard").textContent=withFlow?s.standing:"not re-evaluated";
 $("#matchCard").textContent=withFlow?s.match:"not re-evaluated";
 $("#eprState").textContent="waiting"; $("#epr").className="node epr";
 $("#result").className="result neutral"; $("#result").innerHTML="<strong>READY</strong><span>Run the same proposed consequence through the selected path.</span>";
 controls.innerHTML="";
 if(current==="dependency"&&withFlow) dependencyControls(); else controls.innerHTML='<span class="hint">'+(withFlow?"Current conditions are evaluated at the represented consequence boundary.":"Synthetic comparator: no T1 authority revalidation is performed.")+'</span>';
 $("#receipt").innerHTML=receiptRows([["Decision time","not yet attempted"],["Earlier evidence",s.t0],["Runtime change",s.change],["Decision","—"]]);
 $("#preserveText").textContent="Run the represented commit to create the decision record.";
}
function receiptRows(rows){return rows.map(x=>'<div><span>'+x[0]+'</span><b>'+x[1]+'</b></div>').join("");}
function outcome(){
 const s=scenarios[current]; let reader=s.reader;
 if(current==="dependency"&&withFlow) reader=$("#reader").value;
 let committed,decision,reason,standing;
 if(!withFlow){committed=true;decision="COMPARATOR · COMMITTED";reason="No consequence-time authority revalidation in this synthetic comparator.";standing="NOT RE-EVALUATED";}
 else{
   const exactActive=reader==="ACTIVE", match=s.match==="MATCH";
   committed=exactActive&&match;
   standing=reader;
   decision=committed?"ALLOW · COMMITTED":"REFUSE · NOT COMMITTED";
   reason=!match?"Proposed payload no longer matches the earlier represented object.":reader==="PREVENTED"?"Current standing PREVENTED.":reader==="STRING"?"Plain string ACTIVE rejected; exact standing representation required.":reader==="MISSING"?"Standing reader absent; current standing cannot be established.":reader==="ERROR"?"Standing reader exception; current standing cannot be established.":reader==="ACTIVE"?"Current standing ACTIVE and proposed action matches.":"Current standing cannot be established as exact typed ACTIVE.";
 }
 $("#eprState").textContent=committed?"COMMITTED":"NOT COMMITTED"; $("#epr").classList.add(committed?"committed":"blocked");
 $("#result").className="result "+(committed?"ok":"stop"); $("#result").innerHTML="<strong>"+decision+"</strong><span>"+reason+"</span>";
 const rows=[
 ["Decision time","T1 · represented consequence attempt"],
 ["Actor","epr-writer-A"],
 ["Action","clinical-note.commit"],
 ["Target","synthetic encounter"],
 ["Earlier evidence",s.t0],
 ["Runtime change",s.change],
 ["Current standing",standing],
 ["Payload match",withFlow?s.match:"NOT RE-EVALUATED"],
 ["Determination",decision],
 ["Represented sink",committed?"1 synthetic note":"empty / unchanged"]
 ];
 $("#receipt").innerHTML=receiptRows(rows);
 $("#preserveText").textContent=withFlow?"The record shows the evidence used by the reference-model decision at T1; it is not later reconstruction.":"Comparator record shows that no T1 authority revalidation was performed; this is a synthetic comparison, not a claim about a real product.";
}
document.querySelectorAll("[data-s]").forEach(b=>b.onclick=()=>{document.querySelectorAll("[data-s]").forEach(x=>x.classList.remove("active"));b.classList.add("active");current=b.dataset.s;render();});
$("#withMode").onclick=()=>{withFlow=true;$("#withMode").classList.add("active");$("#withoutMode").classList.remove("active");render();};
$("#withoutMode").onclick=()=>{withFlow=false;$("#withoutMode").classList.add("active");$("#withMode").classList.remove("active");render();};
$("#execute").onclick=outcome; render();
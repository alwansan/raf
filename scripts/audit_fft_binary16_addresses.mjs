export function auditBinary16FftAddresses(){
 const view=new DataView(new ArrayBuffer(2)),rows=[];
 for(const n of [32,64,128,256,512,1024,2048]){
  let changedCenters=0,wrongPointSampleIndex=0,outOfBounds=0,wrongClampedPointSampleIndex=0,crossHalfReads=0;
  for(let i=0;i<2*n;i++){
   const center=(i+0.5)/(2*n);view.setFloat16(0,center,true);
   const q=view.getFloat16(0,true),decoded=Math.floor(q*2*n);
   const clamped=Math.max(0,Math.min(2*n-1,decoded));
   wrongClampedPointSampleIndex+=Number(clamped!==i);
   crossHalfReads+=Number(Math.floor(clamped/n)!==Math.floor(i/n));
   changedCenters+=Number(q!==center);wrongPointSampleIndex+=Number(decoded!==i);outOfBounds+=Number(decoded>=2*n||decoded<0);
  }
  rows.push({resolution:n,width:2*n,changedCenters,wrongPointSampleIndex,outOfBounds,wrongClampedPointSampleIndex,crossHalfReads});
 }
 if(rows.some(r=>r.resolution<=512&&(r.changedCenters||r.wrongPointSampleIndex)))throw Error("Compute-range exactness failed");
 if(rows.filter(r=>r.resolution>512).some(r=>!r.wrongPointSampleIndex||!r.outOfBounds))throw Error("Negative boundary control failed");
 for(const r of rows){
  const expected=r.resolution<=512?[0,0]:r.resolution===1024?[511,0]:[1535,1];
  if(r.wrongClampedPointSampleIndex!==expected[0]||r.crossHalfReads!==expected[1])throw Error("Clamp/bank boundary control failed");
  if(r.wrongPointSampleIndex-r.wrongClampedPointSampleIndex!==r.outOfBounds)throw Error("Clamp correction count failed");
 }
 return {rows,actualUnityOrGpuExecution:false,pointSamplingClampModel:true,hardwareFilteringOrShaderBehaviorVerified:false};
}
console.log(JSON.stringify(auditBinary16FftAddresses(),null,2));

// Physical crates and a temporary cutaway share the fleet's world coordinates.
export function createCargoLoading(T, scene, centerX) {
  const root=new T.Group();root.position.x=centerX;scene.add(root);
  const mat=(color,roughness=.65,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness});
  const ivory=mat(0xe6e6db),steel=mat(0x586c6c,.35,.65),wood=mat(0xad7c42),dark=mat(0x292f22);
  const cutaway=ivory.clone();cutaway.transparent=true;cutaway.depthWrite=false;
  const boxGeo=new T.BoxGeometry(1,1,1);
  function box(parent,x,y,z,w,h,d,material){const m=new T.Mesh(boxGeo,material);m.position.set(x,y,z);m.scale.set(w,h,d);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
  box(root,0,.10,0,12.19,.20,2.44,steel);
  box(root,6.04,1.4,0,.12,2.6,2.44,ivory);
  box(root,0,1.4,-1.22,12.19,2.6,.08,ivory);
  const nearWall=new T.Group();root.add(nearWall);
  box(nearWall,0,1.4,1.22,12.19,2.6,.06,cutaway);
  box(nearWall,0,2.7,0,12.19,.08,2.44,cutaway);
  for(let i=0;i<44;i++){
    box(root,-5.94+i*.276,1.4,-1.26,.055,2.5,.045,ivory);
    box(nearWall,-5.94+i*.276,1.4,1.26,.055,2.5,.045,cutaway);
  }
  // The roof is omitted in the loading cutaway; the solid model returns once sealed.
  for(const z of [-1.22,1.22]){
    box(root,0,2.7,z,12.19,.12,.13,steel);
    box(root,-6.04,1.4,z,.13,2.6,.13,steel);
  }
  const doors=[-1,1].map(side=>{
    const pivot=new T.Group();pivot.position.set(-6.1,0,side*1.22);root.add(pivot);
    box(pivot,0,1.4,-side*.61,.12,2.6,1.2,ivory);
    for(const offset of [.32,.87])box(pivot,-.09,1.4,-side*offset,.055,2.38,.055,steel);
    for(const y of [.45,2.3])box(pivot,-.13,y,-side*.32,.08,.10,.28,steel);
    return pivot;
  });
  // A short roller bed gives the crates a visible support while they enter.
  const conveyor=new T.Group();root.add(conveyor);
  for(const z of [-1.04,1.04])box(conveyor,-8.7,.16,z,5.3,.17,.10,steel);
  const rollerGeo=new T.CylinderGeometry(.065,.065,2.04,10);
  for(let i=0;i<18;i++){
    const roller=new T.Mesh(rollerGeo,steel);roller.rotation.x=Math.PI/2;roller.position.set(-11.1+i*.28,.23,0);conveyor.add(roller);
  }
  const colors=[0xee992f,0x75a824,0xf1af34,0xead24c,0x3e632c,0xd6b330,0xca8d28,0x97b341];
  const fruitGeo=new T.SphereGeometry(1,14,10);
  const crates=colors.map((color,i)=>{
    const crate=new T.Group();root.add(crate);
    box(crate,0,.065,0,1.65,.13,.91,wood);
    box(crate,0,.13,0,1.48,.025,.77,dark);
    for(const x of [-.77,.77])for(const z of [-.40,.40])box(crate,x,.36,z,.11,.67,.10,wood);
    for(const y of [.24,.46,.66]){
      for(const z of [-.435,.435])box(crate,0,y,z,1.65,.13,.065,wood);
      for(const x of [-.80,.80])box(crate,x,y,0,.065,.13,.91,wood);
    }
    const fruits=new T.InstancedMesh(fruitGeo,mat(color,.48),18),dummy=new T.Object3D();
    for(let j=0;j<18;j++){
      dummy.position.set((j%6-2.5)*.235,.54+Math.sin(j*2.7+i)*.025,(Math.floor(j/6)-1)*.24);
      dummy.scale.set(i===2?.11:.14,i===2?.24:i===4?.18:.14,.13);
      dummy.rotation.set(.12*Math.sin(j),j*2.4,.2*Math.cos(j));dummy.updateMatrix();fruits.setMatrixAt(j,dummy.matrix);
    }
    fruits.castShadow=true;fruits.receiveShadow=true;crate.add(fruits);return crate;
  });
  const ease=p=>p*p*(3-2*p),phase=(t,a,b)=>Math.max(0,Math.min(1,(t-a)/(b-a)));
  return {update(time){
    root.visible=time<.445;
    if(!root.visible)return;
    const seal=ease(phase(time,.365,.44));
    cutaway.opacity=.08+.92*seal;nearWall.visible=seal>0;
    doors.forEach((door,i)=>door.rotation.y=(i?1:-1)*1.72*(1-ease(phase(time,.355+i*.018,.425+i*.018))));
    conveyor.position.x=-5*ease(phase(time,.35,.43));
    crates.forEach((crate,i)=>{
      const p=phase(time,.008+i*.027,.16+i*.027),travel=ease(p);
      crate.visible=time>=.008+i*.027;
      crate.position.set(T.MathUtils.lerp(-12.6,4.65-Math.floor(i/2)*2.65,travel),.3,(i%2?1:-1)*.53*ease(phase(p,.3,.85)));
      // Brief suspension-like settling, with no bounce after the crate is stowed.
      crate.position.y+=Math.sin(phase(p,.82,1)*Math.PI)*.025;
    });
  },crates};
}

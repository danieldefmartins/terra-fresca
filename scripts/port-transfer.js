// Match a physical reefer to DOM berth coordinates while the shore crane transfers it.
export function createPortTransfer(T, original, environment) {
  const scene=new T.Scene();scene.environment=environment;scene.environmentIntensity=.85;
  scene.add(new T.HemisphereLight(0xeaf4ff,0x273b43,2));
  const sun=new T.DirectionalLight(0xffefd4,3);sun.position.set(-200,700,300);scene.add(sun);
  const camera=new T.OrthographicCamera();
  const container=original.clone(true);container.position.set(0,0,0);container.rotation.set(0,Math.PI/2,0);container.visible=true;scene.add(container);
  const crane=new T.Group();scene.add(crane);
  const steel=new T.MeshStandardMaterial({color:0x946323,metalness:.55,roughness:.35});
  const cableMat=new T.MeshStandardMaterial({color:0x26383d,metalness:.6,roughness:.35});
  const geo=new T.BoxGeometry(1,1,1);
  const beam=()=>{const m=new T.Mesh(geo,steel);crane.add(m);return m};
  const rails=[beam(),beam()],cross=[beam(),beam()],trolley=beam();
  const spreader=new T.Group();crane.add(spreader);
  const spreaderParts=Array.from({length:5},()=>{const m=new T.Mesh(geo,steel);spreader.add(m);return m});
  const braces=Array.from({length:16},()=>beam());
  const cables=Array.from({length:4},()=>{const m=new T.Mesh(geo,cableMat);crane.add(m);return m});
  const shadow=new T.Mesh(new T.PlaneGeometry(1,1),new T.MeshBasicMaterial({color:0x00151e,transparent:true,opacity:.3,depthWrite:false}));
  shadow.rotation.x=-Math.PI/2;scene.add(shadow);
  const phase=(t,a,b)=>Math.max(0,Math.min(1,(t-a)/(b-a))),ease=p=>p*p*(3-2*p),lerp=T.MathUtils.lerp;
  return {draw(renderer,time,width,height,film){
    const pin=film.querySelector('.film-pin').getBoundingClientRect();
    const from=film.querySelector('#fTrail').getBoundingClientRect(),to=film.querySelector('#filmShipSlot').getBoundingClientRect();
    const point=r=>({x:r.left+r.width/2-pin.left-width/2,z:r.top+r.height/2-pin.top-height/2});
    const start=point(from),end=point(to);
    const lift=ease(phase(time,6.72,6.90)),traverse=ease(phase(time,6.91,7.23)),lower=ease(phase(time,7.23,7.40));
    const land=phase(time,7.40,7.48),altitude=65*lift*(1-lower);
    const baseScale=lerp(Math.max(12,Math.min(from.width,from.height))/2.438,to.width/2.438,ease(phase(time,6.90,7.38)));
    // A slight enlargement and displaced contact shadow make the hoist height legible from above.
    const size=baseScale*(1+.12*lift*(1-lower));
    container.scale.setScalar(size);container.position.set(lerp(start.x,end.x,traverse),altitude,lerp(start.z,end.z,traverse));
    container.rotation.y=Math.PI/2+Math.sin(traverse*Math.PI)*.025*(1-lower);
    const span=Math.max(70,to.width*5.4),x=container.position.x,z=container.position.z;
    const gantryHeight=65+Math.max(12,Math.min(from.width,from.height))/2.438*3.1+110;
    const trolleyZ=z-size*6.1-24;
    const dockZ=-height*.36,reach=Math.max(80,end.z-dockZ+span*.65);
    rails.forEach((m,i)=>{m.position.set(end.x+(i?1:-1)*span*.62,gantryHeight,dockZ+reach/2);m.scale.set(5,9,reach)});
    cross.forEach((m,i)=>{m.position.set(end.x,gantryHeight,dockZ+(i?reach:0));m.scale.set(span*1.3,9,5)});
    trolley.position.set(x,gantryHeight,trolleyZ);trolley.scale.set(span*1.27,9,12);
    spreader.position.set(x,altitude+size*2.7+5+land*65,z);spreaderParts.forEach((m,i)=>{if(i<2){m.position.set((i?1:-1)*size*.91,0,0);m.scale.set(Math.max(1.2,size*.1),3,size*11.3)}else{m.position.set(0,0,(i-3)*size*5.4);m.scale.set(size*2.1,3,Math.max(1.2,size*.1))}});
    const segment=(m,a,b,thickness)=>{const delta=b.clone().sub(a);m.position.copy(a).add(b).multiplyScalar(.5);m.scale.set(thickness,delta.length(),thickness);m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.normalize())};
    cables.forEach((m,i)=>segment(m,new T.Vector3(x+(i%2?1:-1)*span*.55,gantryHeight,trolleyZ),new T.Vector3(x+(i%2?1:-1)*size*.9,spreader.position.y,z+(i<2?1:-1)*size*5.2),.9));
    braces.forEach((m,i)=>{const side=i<8?-1:1,j=i%8,rx=end.x+side*span*.62;segment(m,new T.Vector3(rx-3,gantryHeight,dockZ+j*reach/8),new T.Vector3(rx+3,gantryHeight,dockZ+(j+1)*reach/8),1.3)});
    shadow.position.set(x+altitude*.18,-.1,z+altitude*.3);shadow.scale.set(size*2.44,size*12.19,1);shadow.material.opacity=.32-.18*lift*(1-lower);
    crane.visible=time<7.49;container.visible=time<7.49;shadow.visible=time<7.49;
    camera.left=-width/2;camera.right=width/2;camera.top=height/2;camera.bottom=-height/2;camera.near=.1;camera.far=2000;
    camera.position.set(0,1000,0);camera.up.set(0,0,-1);camera.lookAt(0,0,0);camera.updateProjectionMatrix();
    renderer.render(scene,camera);
    return {lift,traverse,lower,land,gantryClearance:gantryHeight-4.5-(altitude+size*2.7),trolleyScreenClearance:z-size*6.1-(trolleyZ+6),landingError:Math.hypot(x-end.x,z-end.z)};
  }};
}

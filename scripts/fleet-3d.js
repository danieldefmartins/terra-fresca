// A real, articulated fleet in the shipment section. The opening globe is independent.
// Progress sets every mechanical pose directly, so scrubbing backwards is reversible.
const film=document.querySelector('#journeyFilm');
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;

const status={ready:false,mode:'waiting',triangles:0,drawCalls:0,wheelAngle:0,cameraElevation:0};
window.__fleet3d=status;
// Load the model and renderer near the journey, leaving the hero light and responsive.
await new Promise(resolve=>{const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){observer.disconnect();resolve();}},{rootMargin:'1800px'});observer.observe(film);});
const THREE=await import('../vendor/three/three.module.min.js');
const [{GLTFLoader},{RoomEnvironment}]=await Promise.all([import('../vendor/three/GLTFLoader.js'),import('../vendor/three/RoomEnvironment.js')]);
const clamp=THREE.MathUtils.clamp,mix=THREE.MathUtils.lerp;
const phase=(t,a,b)=>clamp((t-a)/(b-a),0,1);
const smooth=(t,a,b)=>{const p=phase(t,a,b);return p*p*(3-2*p)};
let renderer,canvas;
try {
  renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'high-performance'});
  canvas=renderer.domElement;canvas.className='fleet-canvas';
  canvas.setAttribute('aria-hidden','true');
  renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<761?1.5:2));
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;
  renderer.setClearColor(0x000000,0);
  const scene=new THREE.Scene();
  const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();
  const environment=pmrem.fromScene(room,.04);scene.environment=environment.texture;
  scene.environmentIntensity=.85;room.dispose();pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xe9f5ff,0x525a44,1.25));
  const sun=new THREE.DirectionalLight(0xffefcc,3.1);sun.position.set(-5,16,12);
  sun.castShadow=true;sun.shadow.mapSize.set(innerWidth<761?1024:2048,innerWidth<761?1024:2048);
  Object.assign(sun.shadow.camera,{left:-24,right:24,top:20,bottom:-20,near:.1,far:70});
  sun.shadow.bias=-.0002;sun.shadow.normalBias=.035;sun.shadow.radius=3;scene.add(sun);
  const rim=new THREE.DirectionalLight(0x91c5e6,2.2);rim.position.set(10,7,-10);scene.add(rim);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(140,100),new THREE.ShadowMaterial({opacity:.24}));
  floor.rotation.x=-Math.PI/2;floor.position.y=-.015;floor.receiveShadow=true;scene.add(floor);
  const camera=new THREE.OrthographicCamera(-20,20,15,-15,.1,150);
  const target=new THREE.Vector3(-1.1,1.8,0);
  const model=(await new GLTFLoader().loadAsync(new URL('../assets/models/terra-fleet.glb',import.meta.url).href)).scene;
  scene.add(model);
  const truck=model.getObjectByName('truck'),payload=model.getObjectByName('payload');
  const crane=model.getObjectByName('crane'),boom=model.getObjectByName('crane_boom'),spreader=model.getObjectByName('spreader');
  const boomJoint=new THREE.Group();boomJoint.position.copy(boom.position);crane.add(boomJoint);boomJoint.add(boom);boom.position.set(0,0,0);
  payload.rotation.y=Math.PI;
  const extension=model.getObjectByName('crane_extension');
  const truckWheels=[],craneWheels=[];
  model.traverse(o=>{
    if(o.name.includes('_wheel_')&&!o.parent?.name.includes('_wheel_'))(o.name.startsWith('crane')?craneWheels:truckWheels).push(o);
    if(o.isMesh){o.castShadow=true;o.receiveShadow=true;
      for(const m of Array.isArray(o.material)?o.material:[o.material]){
        if(m.name==='paint'){m.color.set('#073b46');m.roughness=.27;m.metalness=.4;}
        if(m.name==='tyre'){m.color.set('#14191c');m.roughness=.87;}
        if(m.name==='rim'){m.color.set('#aeb8bf');m.roughness=.24;m.metalness=.85;}
        if(m.name==='glass'){m.color.set('#123d51');m.roughness=.08;m.metalness=.35;}
      }
    }
  });
  const cranePaint=new THREE.MeshStandardMaterial({color:0xc39438,roughness:.3,metalness:.35});
  crane.traverse(o=>{if(o.isMesh){if(Array.isArray(o.material))o.material=o.material.map(m=>m.name==='paint'?cranePaint:m);else if(o.material.name==='paint')o.material=cranePaint;}});
  model.updateMatrixWorld(true);
  const wheelCenter=wheel=>wheel.parent.worldToLocal(new THREE.Box3().setFromObject(wheel).getCenter(new THREE.Vector3()));
  const axleCenters=truckWheels.map(wheelCenter);
  status.checkAxles=()=>{model.updateMatrixWorld(true);return Math.max(...truckWheels.map((wheel,i)=>wheelCenter(wheel).distanceTo(axleCenters[i])))};
  // Decals are textures on the model's two physical side walls, not screen overlays.
  const labelTexture=await new THREE.TextureLoader().loadAsync(new URL('../assets/tf-lockup.webp',import.meta.url).href);
  labelTexture.colorSpace=THREE.SRGBColorSpace;
  labelTexture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
  const decalMaterial=new THREE.MeshStandardMaterial({map:labelTexture,transparent:true,depthWrite:false,roughness:.6,polygonOffset:true,polygonOffsetFactor:-2});
  for(const side of [-1,1]){
    const decal=new THREE.Mesh(new THREE.PlaneGeometry(8.2,8.2*labelTexture.image.height/labelTexture.image.width),decalMaterial);
    decal.position.set(0,1.42,side*1.241);if(side<0)decal.rotation.y=Math.PI;
    payload.add(decal);
  }
  const cabLogo=await new THREE.TextureLoader().loadAsync(new URL('../assets/tf-mark-light.webp',import.meta.url).href);
  cabLogo.colorSpace=THREE.SRGBColorSpace;
  for(const side of [-1,1]){
    const mark=new THREE.Mesh(new THREE.PlaneGeometry(.44,.44*cabLogo.image.height/cabLogo.image.width),new THREE.MeshStandardMaterial({map:cabLogo,transparent:true,depthWrite:false,roughness:.55}));
    mark.position.set(5.9,1.91,side*1.27);if(side<0)mark.rotation.y=Math.PI;truck.add(mark);
  }
  // Hoist links remain connected to the spreader as the payload rises and settles.
  const linkMaterial=new THREE.MeshStandardMaterial({color:0x9eacaa,metalness:.8,roughness:.25});
  const links=Array.from({length:4},()=>{const m=new THREE.Mesh(new THREE.CylinderGeometry(.025,.025,1,8),linkMaterial);scene.add(m);return m});
  const hydraulics=Array.from({length:4},(_,i)=>{const m=new THREE.Mesh(new THREE.CylinderGeometry(i%2?.065:.13,i%2?.065:.13,1,12),new THREE.MeshStandardMaterial({color:i%2?0xcbd6d7:0x34464b,metalness:.8,roughness:.22}));scene.add(m);return m;});
  const up=new THREE.Vector3(0,1,0),a=new THREE.Vector3(),b=new THREE.Vector3(),direction=new THREE.Vector3();
  function setLink(mesh,from,to){direction.subVectors(to,from);mesh.position.copy(from).add(to).multiplyScalar(.5);mesh.scale.set(1,direction.length(),1);mesh.quaternion.setFromUnitVectors(up,direction.normalize());}
  let filmVisible=false,width=0,height=0,dirty=true,lastTime=-1;
  const observer=new IntersectionObserver(entries=>{filmVisible=entries[0].isIntersecting;dirty=true;});observer.observe(film);
  film.querySelector('.film-pin').append(canvas);
  addEventListener('resize',()=>{width=0;dirty=true});
  const poseCamera=(az,el,viewHeight,cx,cy)=>{
    const half=viewHeight/2;camera.left=-half*width/height;camera.right=half*width/height;camera.top=half;camera.bottom=-half;
    camera.position.set(target.x+Math.sin(az)*Math.cos(el)*40,target.y+Math.sin(el)*40,target.z+Math.cos(az)*Math.cos(el)*40);
    camera.up.set(0,1,0);camera.lookAt(target);
    camera.setViewOffset(width,height,width/2-cx,height/2-cy,width,height);camera.updateProjectionMatrix();status.cameraElevation=el;
  };
  const payloadBase=payload.position.clone();
  const {createCargoLoading}=await import('./cargo-loading.js');
  const cargo=createCargoLoading(THREE,scene,payloadBase.x);
  const {createPortTransfer}=await import('./port-transfer.js');
  const port=createPortTransfer(THREE,payload,environment.texture);
  function draw(now){
    requestAnimationFrame(draw);
    if(!status.ready||document.hidden||!filmVisible)return;
    const time=window.__film?.().t||0;
    const next='film';status.mode=next;
    if(next==='film'&&(time>=7.49||!filmVisible)){canvas.style.visibility='hidden';film.classList.remove('fleet-active','port-active');return;}
    canvas.style.visibility='visible';
    const parent=canvas.parentElement,w=parent.clientWidth,h=parent.clientHeight;
    if(width!==w||height!==h){width=w;height=h;renderer.setSize(w,h,false);dirty=true;}
    if(reduced&&!dirty&&time===lastTime)return;
    if(!dirty&&now-(status.lastFrame||0)<(width<761?42:30))return;
    status.lastFrame=now;lastTime=time;dirty=false;
    const mobile=width<=760;
    film.classList.toggle('port-active',time>=6.72);
    if(time>=6.72){film.classList.add('fleet-active');status.port=port.draw(renderer,time,width,height,film);status.time=time;return;}
    target.x=mix(mobile?-3:-1.1,-1.1,smooth(time,1.30,1.68));
    truck.position.set(0,0,0);truck.rotation.set(0,0,0);payload.position.copy(payloadBase);
    cargo.update(time);truck.children.forEach(child=>child.visible=child===payload||time>=.82);payload.visible=time>=.445;status.loadingCrates=cargo.crates.filter(c=>c.visible).length;
    crane.visible=next==='film'&&time>=.44&&time<1.66;spreader.visible=crane.visible;
    links.concat(hydraulics).forEach(l=>l.visible=crane.visible);
    {
      film.classList.add('fleet-active');
      const lift=4.4*smooth(time,.70,.90)*(1-smooth(time,1.04,1.24));
      const deck=1.305*smooth(time,1.04,1.24);
      payload.position.y=time<1.24?lift+deck:payloadBase.y;
      truck.position.x=31*(1-smooth(time,.82,1.12));
      // The payload is owned by the truck node; cancel its reversing motion until seated.
      payload.position.x=payloadBase.x-truck.position.x;
      const recoil=Math.sin(phase(time,1.18,1.32)*Math.PI)*.08;
      if(time>=1.18&&time<=1.32)truck.position.y=-recoil;
      crane.position.set(-10-24*(1-smooth(time,.44,.64))-25*smooth(time,1.3,1.66),0,3);
      crane.rotation.y=.35;
      spreader.position.set(payloadBase.x+crane.position.x+10,payload.position.y+2.91,0);
      if(time>1.24)spreader.position.y+=2*smooth(time,1.24,1.35);
      boomJoint.rotation.z=Math.atan2(spreader.position.y-2.35,8.6)-.52;
      extension.scale.z=.84+.16*smooth(time,.62,.92);
      crane.updateMatrixWorld(true);
      for(let side=0;side<2;side++){
        const z=side?-.65:.65;
        const start=new THREE.Vector3(-1.1,1.65,z),end=new THREE.Vector3(3,4.55,z);
        end.sub(new THREE.Vector3(-1.6,2.35,-.4)).applyAxisAngle(new THREE.Vector3(0,0,1),boomJoint.rotation.z).add(new THREE.Vector3(-1.6,2.35,-.4));
        crane.localToWorld(start);crane.localToWorld(end);
        const middle=start.clone().lerp(end,.62);setLink(hydraulics[side*2],start,middle);setLink(hydraulics[side*2+1],middle,end);
      }
      const boomTip=new THREE.Vector3(7.6,7.67,-.4).sub(new THREE.Vector3(-1.6,2.35,-.4));
      boomTip.applyAxisAngle(new THREE.Vector3(0,0,1),boomJoint.rotation.z).add(new THREE.Vector3(-1.6,2.35,-.4));crane.localToWorld(boomTip);
      links.forEach((link,i)=>{a.copy(boomTip);a.x+=(i<2?-.25:.25);a.z+=i%2?.2:-.2;b.copy(spreader.position);b.x+=i<2?-4.3:4.3;b.z+=i%2?1:-1;setLink(link,a,b)});
      const travel=truck.position.x+Math.max(0,time-1.32)*14;
      truckWheels.forEach(w=>w.rotation.z=-travel/.525);
      craneWheels.forEach(w=>w.rotation.z=-crane.position.x/.709);
      status.wheelAngle=-travel/.525;
      if(time<3.7){
        const care=smooth(time,1.30,1.68);
        poseCamera(mix(mix(-.88,.48,smooth(time,.36,.62)),.22,care)+Math.sin(phase(time,1.7,3.6)*Math.PI)*.18,mix(mix(.40,.33,smooth(time,.36,.62)),.17,care),mix(mix(mobile?35:22,mobile?52:27,smooth(time,.36,.62)),17.5*height/(width*(mobile?.94:.61)),care),width*(mobile?.5:.61),height*mix(mix(.52,.66,smooth(time,.36,.62)),mobile?.31:.285,care));
      }else{
        const orbit=smooth(time,3.7,4.30);
        let cx=width*.5,cy=height*.41,span=width*.11,angle=0;
        const cab=document.querySelector('#fCab').getBoundingClientRect(),trail=document.querySelector('#fTrail').getBoundingClientRect();
        const pin=film.querySelector('.film-pin').getBoundingClientRect();
        if(cab.width&&trail.width){
          cx=(Math.min(cab.left,trail.left)+Math.max(cab.right,trail.right))/2-pin.left;
          cy=(Math.min(cab.top,trail.top)+Math.max(cab.bottom,trail.bottom))/2-pin.top;
          span=Math.hypot(Math.max(cab.right,trail.right)-Math.min(cab.left,trail.left),Math.max(cab.bottom,trail.bottom)-Math.min(cab.top,trail.top));
          angle=Math.atan2(cab.top+cab.height/2-trail.top-trail.height/2,cab.left+cab.width/2-trail.left-trail.width/2);
        }
        poseCamera(mix(.22,0,orbit),mix(.17,Math.PI/2-.001,orbit),mix(17.5*height/(width*(mobile?.94:.61)),17*height/span,orbit),mix(width*(mobile?.5:.61),cx,orbit),mix(height*(mobile?.31:.285),cy,orbit));
        truck.rotation.y=-angle*orbit;
      }
    }
    renderer.render(scene,camera);
    status.triangles=renderer.info.render.triangles;status.drawCalls=renderer.info.render.calls;status.time=time;
  }
  renderer.compile(scene,camera);
  status.ready=true;status.wheels=truckWheels.length;status.craneWheels=craneWheels.length;

  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();status.ready=false;film.classList.remove('fleet-active','port-active');canvas.style.display='none'});
  requestAnimationFrame(draw);
}catch(error){
  status.error=String(error);console.error('3D fleet unavailable; retaining illustrated journey.',error);
  film.classList.remove('fleet-active','port-active');canvas?.remove();renderer?.dispose();
}

// NASA Blue Marble, September 2004, with topographic shading. See assets/EARTH-CREDIT.md.
import * as T from '../vendor/three/three.module.min.js';
export async function createEarthGlobe(){
  const renderer=new T.WebGLRenderer({alpha:true,antialias:true,preserveDrawingBuffer:true,powerPreference:'low-power'});
  try {
    const texture=await new T.TextureLoader().loadAsync(new URL('../assets/earth-topography.jpg',import.meta.url).href);
    texture.colorSpace=T.SRGBColorSpace;texture.wrapS=T.RepeatWrapping;
    const uniforms={earth:{value:texture},rotation:{value:0},tilt:{value:.22}};
    const material=new T.ShaderMaterial({transparent:true,uniforms,
      vertexShader:'varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position.xy,0.0,1.0);}',
      fragmentShader:`
        uniform sampler2D earth;uniform float rotation;uniform float tilt;varying vec2 vUv;
        void main(){
          vec2 p=vUv*2.0-1.0;float r2=dot(p,p);if(r2>1.0)discard;
          float z=sqrt(max(0.0,1.0-r2));
          float latitude=asin(clamp(p.y*cos(tilt)+z*sin(tilt),-1.0,1.0));
          float longitude=atan(p.x,z*cos(tilt)-p.y*sin(tilt))-rotation;
          vec2 uv=vec2(fract(longitude/6.28318530718+.5),latitude/3.14159265359+.5);
          vec3 color=texture2D(earth,uv).rgb;
          // Deep blue ocean catches light; topographic shading remains in the source map.
          float ocean=smoothstep(.0001,.0045,color.b-max(color.r,color.g))*(1.0-smoothstep(.025,.12,max(color.r,max(color.g,color.b))));
          color=mix(color,vec3(.008,.065,.20),ocean*.70);
          float diffuse=max(0.0,dot(vec3(p,z),normalize(vec3(-.45,.55,1.0))));
          color*=.32+diffuse*.96;
          float rim=pow(1.0-z,3.5);
          color=mix(color,vec3(.06,.30,.58),rim*.48);
          gl_FragColor=vec4(color,1.0-smoothstep(.992,1.0,r2));
          #include <colorspace_fragment>
        }`});
    const scene=new T.Scene(),camera=new T.Camera();scene.add(new T.Mesh(new T.PlaneGeometry(2,2),material));
    let pixels=0,lost=false,lastFrame=-Infinity,lastRotation=Infinity,lastTilt=Infinity;
    renderer.domElement.addEventListener('webglcontextlost',event=>{event.preventDefault();lost=true});
    renderer.setClearColor(0,0);
    return {draw(ctx,cx,cy,radius,rotation,tilt){
      if(lost)return false;
      const size=Math.min(1200,Math.ceil(radius*2*Math.min(devicePixelRatio,1.5)));
      const now=performance.now();
      if(pixels!==size||now-lastFrame>32||Math.abs(rotation-lastRotation)>.006||Math.abs(tilt-lastTilt)>.006){
        if(pixels!==size){pixels=size;renderer.setSize(size,size,false)}
        uniforms.rotation.value=rotation;uniforms.tilt.value=tilt;
        renderer.render(scene,camera);lastFrame=now;lastRotation=rotation;lastTilt=tilt;
      }
      ctx.drawImage(renderer.domElement,cx-radius,cy-radius,radius*2,radius*2);return true;
    }};
  }catch(error){renderer.dispose();throw error;}
}

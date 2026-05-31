import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useMemo, useRef, Suspense } from "react";
import * as THREE from "three";

/* ---------- lightweight 3D value-noise (deterministic) ---------- */
function hash(x: number, y: number, z: number) {
  let h = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453;
  return h - Math.floor(h);
}
function smooth(t: number) {
  return t * t * (3 - 2 * t);
}
function noise3(x: number, y: number, z: number) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const u = smooth(xf), v = smooth(yf), w = smooth(zf);
  const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
  const c000 = hash(xi, yi, zi);
  const c100 = hash(xi + 1, yi, zi);
  const c010 = hash(xi, yi + 1, zi);
  const c110 = hash(xi + 1, yi + 1, zi);
  const c001 = hash(xi, yi, zi + 1);
  const c101 = hash(xi + 1, yi, zi + 1);
  const c011 = hash(xi, yi + 1, zi + 1);
  const c111 = hash(xi + 1, yi + 1, zi + 1);
  return lerp(
    lerp(lerp(c000, c100, u), lerp(c010, c110, u), v),
    lerp(lerp(c001, c101, u), lerp(c011, c111, u), v),
    w,
  );
}
function fbm(x: number, y: number, z: number) {
  return (
    noise3(x, y, z) * 0.6 +
    noise3(x * 2.1, y * 2.1, z * 2.1) * 0.3 +
    noise3(x * 4.3, y * 4.3, z * 4.3) * 0.1
  );
}

/* ---------- procedural brain point cloud ---------- */
type Region = "cerebrum" | "cerebellum" | "stem";

function sampleHemisphere(
  count: number,
  side: 1 | -1,
  seed: number,
): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  // ellipsoid radii (cerebrum)
  const rx = 1.0, ry = 0.85, rz = 1.15;
  let i = 0;
  let n = 0;
  while (pts.length < count && n < count * 8) {
    n++;
    // fibonacci on sphere, then squash to ellipsoid, then keep one hemisphere (x*side >= -0.02 to leave fissure)
    const idx = i + seed;
    const phi = Math.acos(1 - (2 * (idx + 0.5)) / (count * 2));
    const theta = Math.PI * (1 + Math.sqrt(5)) * idx;
    i++;
    let x = Math.sin(phi) * Math.cos(theta);
    let y = Math.cos(phi);
    let z = Math.sin(phi) * Math.sin(theta);
    // tilt brain forward slightly (z axis is front-back)
    if (x * side < 0.04) continue; // fissure gap
    x *= rx; y *= ry; z *= rz;
    // gyri/sulci displacement: two-octave noise, stronger ridges
    const nx = x * 1.6, ny = y * 1.6, nz = z * 1.6;
    const wrinkle =
      (fbm(nx + seed * 13, ny, nz) - 0.5) * 0.18 +
      (noise3(nx * 3.2, ny * 3.2, nz * 3.2) - 0.5) * 0.09;
    // displace along radial normal of ellipsoid
    const len = Math.hypot(x, y, z) || 1;
    const dx = (x / len) * wrinkle;
    const dy = (y / len) * wrinkle;
    const dz = (z / len) * wrinkle;
    // taper underside (flatter bottom like real brain)
    const yScale = y < -0.2 ? 0.78 : 1.0;
    pts.push(new THREE.Vector3(x + dx, (y + dy) * yScale, z + dz));
  }
  return pts;
}

function sampleCerebellum(count: number): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  const cx = 0, cy = -0.55, cz = -0.82;
  const rx = 0.55, ry = 0.32, rz = 0.45;
  for (let i = 0; i < count; i++) {
    const phi = Math.acos(1 - (2 * (i + 0.5)) / count);
    const theta = Math.PI * (1 + Math.sqrt(5)) * i;
    let x = Math.sin(phi) * Math.cos(theta) * rx;
    let y = Math.cos(phi) * ry;
    let z = Math.sin(phi) * Math.sin(theta) * rz;
    // tight horizontal folia
    const fold = Math.sin(y * 28) * 0.025;
    const len = Math.hypot(x, y, z) || 1;
    x += (x / len) * fold;
    y += (y / len) * fold;
    z += (z / len) * fold;
    pts.push(new THREE.Vector3(cx + x, cy + y, cz + z));
  }
  return pts;
}

function sampleStem(count: number): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  for (let i = 0; i < count; i++) {
    const t = i / count;
    const y = -0.78 - t * 0.55;
    const r = 0.18 - t * 0.08;
    const a = Math.random() * Math.PI * 2;
    pts.push(new THREE.Vector3(Math.cos(a) * r, y, -0.78 + Math.sin(a) * r * 0.9));
  }
  return pts;
}

function buildBrain(scale: number) {
  // scale controls point counts (perf)
  const halfCount = Math.floor(1100 * scale);
  const left = sampleHemisphere(halfCount, -1, 0);
  const right = sampleHemisphere(halfCount, 1, 100);
  const cereb = sampleCerebellum(Math.floor(680 * scale));
  const stem = sampleStem(Math.floor(80 * scale));
  const all = [...left, ...right, ...cereb, ...stem];

  // ember accents: pick cortical landmarks
  const emberPicks: THREE.Vector3[] = [];
  const landmarks = [
    new THREE.Vector3(0.6, 0.55, 0.9),   // frontal R
    new THREE.Vector3(-0.6, 0.55, 0.9),  // frontal L
    new THREE.Vector3(0.85, 0.2, 0.1),   // temporal R
    new THREE.Vector3(-0.85, 0.2, 0.1),  // temporal L
    new THREE.Vector3(0.55, 0.7, -0.5),  // parietal R
    new THREE.Vector3(-0.55, 0.7, -0.5), // parietal L
    new THREE.Vector3(0.4, 0.3, -1.0),   // occipital R
    new THREE.Vector3(-0.4, 0.3, -1.0),  // occipital L
    new THREE.Vector3(0.75, 0.65, 0.4),
    new THREE.Vector3(-0.75, 0.65, 0.4),
    new THREE.Vector3(0.3, 0.85, 0.3),
    new THREE.Vector3(-0.3, 0.85, 0.3),
    new THREE.Vector3(0.0, -0.4, -0.95), // cerebellum mid
    new THREE.Vector3(0.0, -1.15, -0.78), // brain stem tip
  ];
  for (const lm of landmarks) {
    let best = all[0];
    let bestD = Infinity;
    for (const p of all) {
      const d = p.distanceToSquared(lm);
      if (d < bestD) { bestD = d; best = p; }
    }
    emberPicks.push(best.clone());
  }

  // positions buffer
  const positions = new Float32Array(all.length * 3);
  all.forEach((p, i) => {
    positions[i * 3] = p.x;
    positions[i * 3 + 1] = p.y;
    positions[i * 3 + 2] = p.z;
  });

  const emberPositions = new Float32Array(emberPicks.length * 3);
  emberPicks.forEach((p, i) => {
    emberPositions[i * 3] = p.x;
    emberPositions[i * 3 + 1] = p.y;
    emberPositions[i * 3 + 2] = p.z;
  });

  // neural connections: each point to its 2 nearest neighbors (within region buckets, capped distance)
  // To keep it perf-sane, we spatial-hash by cell.
  const cell = 0.18;
  const grid = new Map<string, number[]>();
  const key = (p: THREE.Vector3) =>
    `${Math.floor(p.x / cell)},${Math.floor(p.y / cell)},${Math.floor(p.z / cell)}`;
  all.forEach((p, i) => {
    const k = key(p);
    const arr = grid.get(k);
    if (arr) arr.push(i); else grid.set(k, [i]);
  });

  const linePos: number[] = [];
  const maxDist = 0.22;
  const maxDist2 = maxDist * maxDist;
  for (let i = 0; i < all.length; i++) {
    const p = all[i];
    const cx = Math.floor(p.x / cell);
    const cy = Math.floor(p.y / cell);
    const cz = Math.floor(p.z / cell);
    let best1 = -1, best2 = -1;
    let d1 = Infinity, d2 = Infinity;
    for (let dx = -1; dx <= 1; dx++)
      for (let dy = -1; dy <= 1; dy++)
        for (let dz = -1; dz <= 1; dz++) {
          const arr = grid.get(`${cx + dx},${cy + dy},${cz + dz}`);
          if (!arr) continue;
          for (const j of arr) {
            if (j <= i) continue;
            const d = all[i].distanceToSquared(all[j]);
            if (d > maxDist2) continue;
            if (d < d1) { d2 = d1; best2 = best1; d1 = d; best1 = j; }
            else if (d < d2) { d2 = d; best2 = j; }
          }
        }
    if (best1 >= 0) {
      const q = all[best1];
      linePos.push(p.x, p.y, p.z, q.x, q.y, q.z);
    }
    if (best2 >= 0) {
      const q = all[best2];
      linePos.push(p.x, p.y, p.z, q.x, q.y, q.z);
    }
  }

  const lineGeom = new THREE.BufferGeometry();
  lineGeom.setAttribute("position", new THREE.Float32BufferAttribute(linePos, 3));

  return { positions, emberPositions, lineGeom };
}

function Brain({ scale = 1 }: { scale?: number }) {
  const group = useRef<THREE.Group>(null);
  const linesRef = useRef<THREE.LineSegments>(null);
  const emberRef = useRef<THREE.Points>(null);
  const { mouse } = useThree();

  const { positions, emberPositions, lineGeom } = useMemo(() => buildBrain(scale), [scale]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (group.current) {
      group.current.rotation.y = -0.55 + t * 0.04; // 3/4 left view, slow rotation
      group.current.rotation.x = -0.15 + Math.sin(t * 0.15) * 0.04;
      const tx = mouse.x * 0.25;
      const ty = mouse.y * 0.15;
      group.current.position.x += (tx - group.current.position.x) * 0.04;
      group.current.position.y += (ty - group.current.position.y) * 0.04;
    }
    if (linesRef.current) {
      (linesRef.current.material as THREE.LineBasicMaterial).opacity =
        0.36 + Math.sin(t * 0.5) * 0.05;
    }
    if (emberRef.current) {
      (emberRef.current.material as THREE.PointsMaterial).size =
        0.11 + Math.sin(t * 1.4) * 0.025;
    }
  });

  return (
    <group ref={group} scale={2.1}>
      <lineSegments ref={linesRef} geometry={lineGeom}>
        <lineBasicMaterial color="#0d0d0d" transparent opacity={0.4} depthWrite={false} />
      </lineSegments>
      <points>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        </bufferGeometry>
        <pointsMaterial size={0.035} color="#0d0d0d" sizeAttenuation depthWrite={false} />
      </points>
      <points ref={emberRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[emberPositions, 3]} />
        </bufferGeometry>
        <pointsMaterial
          size={0.11}
          color="#e85d3a"
          sizeAttenuation
          depthWrite={false}
          transparent
          opacity={0.95}
        />
      </points>
    </group>
  );
}

export function AtlasScene({ reduced = false }: { reduced?: boolean }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 6.5], fov: 50 }}
      dpr={[1, 1.6]}
      gl={{ antialias: true, alpha: true }}
      style={{ background: "transparent" }}
    >
      <Suspense fallback={null}>
        <Brain scale={reduced ? 0.55 : 1} />
      </Suspense>
    </Canvas>
  );
}

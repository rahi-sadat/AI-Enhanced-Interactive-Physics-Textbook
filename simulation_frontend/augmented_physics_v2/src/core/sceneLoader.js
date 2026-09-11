/** core/sceneLoader.js - Fetches scene JSON with cache-busting. */
export async function loadScene(url) {
  url = url || '/scenes/kinematics/physics_scene.json';
  const res = await fetch(url + '?t=' + Date.now());
  if (!res.ok) throw new Error('Cannot load scene ' + url + ': ' + res.status);
  return res.json();
}

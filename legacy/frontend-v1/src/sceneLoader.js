export async function loadScene() {

  const response = await fetch(`/physics_scene.json?t=${Date.now()}`);

  if (!response.ok) {
    throw new Error(
      `Could not load physics_scene.json: ${response.status}`
    );
  }

  const scene = await response.json();

  return scene;
}
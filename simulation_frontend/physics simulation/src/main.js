import "./style.css";
import decomp from "poly-decomp";
import { Common } from "matter-js";

Common.setDecomp(decomp);

import {
  loadScene
} from "./sceneLoader.js";

import {
  Simulation
} from "./simulation.js";


async function main() {

  try {

    // --------------------------------
    // Get simulation container
    // --------------------------------

    const container =
      document.getElementById(
        "simulation-container"
      );


    // --------------------------------
    // Create simulation
    // --------------------------------

    const simulation =
      new Simulation(container);


    // --------------------------------
    // Load JSON scene
    // --------------------------------

    const scene =
      await loadScene();


    // --------------------------------
    // Load scene into Matter.js
    // --------------------------------

    simulation.loadScene(scene);

    // --------------------------------
    // Load background diagram image
    // --------------------------------

    const diagramImage = document.getElementById("diagram-image");
    if (diagramImage && scene.visual?.background_url) {
      diagramImage.src = `${scene.visual.background_url}?t=${Date.now()}`;
      diagramImage.style.display = "block";
    }

    // =================================
    // PLAY BUTTON
    // =================================

    document
      .getElementById("play-button")
      .addEventListener(
        "click",
        () => {

          simulation.play();
        }
      );


    // =================================
    // PAUSE BUTTON
    // =================================

    document
      .getElementById("pause-button")
      .addEventListener(
        "click",
        () => {

          simulation.pause();
        }
      );


    // =================================
    // RESET BUTTON
    // =================================

    document
      .getElementById("reset-button")
      .addEventListener(
        "click",
        () => {

          simulation.reset();
        }
      );


    // =================================
    // TOGGLE COLLIDERS (DEBUG)
    // =================================

    const colliderToggle = document.getElementById("toggle-colliders");
    if (colliderToggle) {
      colliderToggle.addEventListener("change", (e) => {
        simulation.setWireframes(e.target.checked);
      });
    }


    // =================================
    // GRAVITY SLIDER
    // =================================

    const gravitySlider =
      document.getElementById(
        "gravity-slider"
      );

    const gravityValue =
      document.getElementById(
        "gravity-value"
      );


    gravitySlider.addEventListener(
      "input",
      () => {

        const value =
          gravitySlider.value;

        simulation.setGravity(value);

        gravityValue.textContent =
          value;
      }
    );


    // =================================
    // SPEED SLIDER
    // =================================

    const speedSlider =
      document.getElementById(
        "speed-slider"
      );

    const speedValue =
      document.getElementById(
        "speed-value"
      );


    speedSlider.addEventListener(
      "input",
      () => {

        const value =
          speedSlider.value;

        simulation.setSpeed(value);

        speedValue.textContent =
          `${value}x`;
      }
    );


    // =================================
    // DYNAMIC OBJECT SELECTOR & VELOCITY SLIDER
    // =================================

    const targetSelect = document.getElementById("target-object-select");
    const dynamicObjects = (scene.objects || []).filter(o => o.role === "dynamic");

    if (targetSelect) {
      targetSelect.innerHTML = "";
      dynamicObjects.forEach((obj, idx) => {
        const opt = document.createElement("option");
        opt.value = obj.id;
        opt.textContent = `${obj.id} (${obj.type})`;
        if (idx === 0) opt.selected = true;
        targetSelect.appendChild(opt);
      });
    }

    const velocitySlider =
      document.getElementById(
        "velocity-slider"
      );

    const velocityValue =
      document.getElementById(
        "velocity-value"
      );

    const getSelectedObjectId = () => {
      return targetSelect && targetSelect.value ? targetSelect.value : (dynamicObjects[0]?.id || null);
    };

    velocitySlider.addEventListener(
      "input",
      () => {
        const value = velocitySlider.value;
        const targetId = getSelectedObjectId();
        if (targetId) {
          simulation.setObjectVelocity(targetId, value);
        }
        velocityValue.textContent = `${value} m/s`;
      }
    );

    // =================================
    // APPLY VELOCITY ON RESET
    // =================================

    document
      .getElementById("apply-velocity-button")
      .addEventListener(
        "click",
        () => {
          const targetId = getSelectedObjectId();
          if (targetId) {
            simulation.setObjectVelocity(targetId, velocitySlider.value);
            console.log(`Velocity of ${targetId} changed to:`, velocitySlider.value);
          }
        }
      );


    console.log(
      "Application started successfully"
    );

  } catch (error) {

    console.error(
      "Application failed:",
      error
    );
  }
}


main();
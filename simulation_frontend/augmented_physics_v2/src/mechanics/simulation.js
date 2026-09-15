import {
  Engine,
  Render,
  Runner,
  Composite,
  Body,
  Events
} from "matter-js";

import {
  createPhysicsBody,
  createSpringSystem,
  createPendulumSystem
} from "./physicsBodyFactory.js";
import { MatterUnitAdapter } from "../core/matterUnitAdapter.js";


export class Simulation {

  constructor(container) {

    this.container = container;

    // -----------------------------
    // Create Matter.js engine & solver settings
    // -----------------------------

    this.engine = Engine.create();
    this.engine.positionIterations = 10;
    this.engine.velocityIterations = 8;
    this.engine.constraintIterations = 4;
    this.unitAdapter = new MatterUnitAdapter(100);

    // -----------------------------
    // Create renderer
    // -----------------------------

    this.render = Render.create({

      element: this.container,

      engine: this.engine,

      options: {
        width: 800,
        height: 600,

        wireframes: false,

        background: "transparent"
      }
    });

    Render.run(this.render);


    // -----------------------------
    // Create high-precision runner (120 Hz fixed timestep)
    // -----------------------------

    this.runner = Runner.create({ delta: 1000 / 120 });


    // -----------------------------
    // Store scene
    // -----------------------------

    this.scene = null;


    // -----------------------------
    // Store bodies and spring systems
    // -----------------------------

    this.bodies = [];
    this.springSystems = [];


    // -----------------------------
    // Track running state
    // -----------------------------

    this.isRunning = false;

    // -----------------------------
    // Constrain spring plungers to 1D horizontal movement
    // -----------------------------
    Events.on(this.engine, "beforeUpdate", () => {
      for (const system of this.springSystems) {
        const plunger = system.plunger;
        if (!plunger) continue;

        // Keep plunger at horizontal equilibrium line
        Body.setPosition(plunger, {
          x: plunger.position.x,
          y: system.restY
        });

        Body.setVelocity(plunger, {
          x: plunger.velocity.x,
          y: 0
        });

        Body.setAngle(plunger, 0);
        Body.setAngularVelocity(plunger, 0);
      }
    });
  }


  // =================================
  // LOAD SCENE
  // =================================

  loadScene(scene, mapper = null) {

    this.scene = scene;
    this.mapper = mapper;


    // Clear previous objects

    Composite.clear(
      this.engine.world,
      false
    );


    this.bodies = [];
    this.springSystems = [];


    // -----------------------------
    // Configure gravity & units
    // -----------------------------

    const ppm = scene.calibration?.pixels_per_meter || 100;
    this.unitAdapter.setPixelsPerMeter(ppm);

    const g = scene.environment?.gravity_m_s2 ??
      (scene.environment?.gravity !== undefined ? (scene.environment.gravity === 1.0 ? 9.81 : scene.environment.gravity) : 9.81);
    this.unitAdapter.setGravity(this.engine, g);


    // -----------------------------
    // Create every object
    // -----------------------------

    for (const object of scene.objects) {

      if (object.type === "spring") {
        const system = createSpringSystem(object);
        Composite.add(this.engine.world, [
          system.plunger,
          system.spring
        ]);
        this.springSystems.push(system);
        this.bodies.push(system.plunger);
        continue;
      }

      if (object.type === "pendulum") {
        const pSystem = createPendulumSystem(object);
        Composite.add(this.engine.world, [
          pSystem.pivot,
          pSystem.bob,
          pSystem.rod
        ]);
        this.bodies.push(pSystem.bob);
        continue;
      }

      const body =
        createPhysicsBody(object);


      if (body) {

        Composite.add(
          this.engine.world,
          body
        );

        this.bodies.push(body);
      }
    }


    console.log(
      "Scene loaded:",
      scene
    );
  }


  // =================================
  // PLAY
  // =================================

  play() {

    if (!this.isRunning) {

      Runner.run(
        this.runner,
        this.engine
      );

      this.isRunning = true;

      console.log("Simulation started");
    }
  }


  // =================================
  // PAUSE
  // =================================

  pause() {

    if (this.isRunning) {

      Runner.stop(
        this.runner
      );

      this.isRunning = false;

      console.log("Simulation paused");
    }
  }


  // =================================
  // RESET
  // =================================

  reset() {

    // Stop simulation

    this.pause();


    // Reload original scene

    if (this.scene) {

      this.loadScene(
        structuredClone(this.scene)
      );
    }


    console.log(
      "Simulation reset"
    );
  }


  // =================================
  // CHANGE GRAVITY
  // =================================

  setGravity(value) {
    this.unitAdapter.setGravity(this.engine, Number(value));
  }


  // =================================
  // CHANGE TIME SPEED
  // =================================

  setSpeed(value) {

    this.engine.timing.timeScale =
      Number(value);
  }


  // =================================
  // SET OBJECT VELOCITY
  // =================================

  setObjectVelocity(
    objectId,
    velocityX
  ) {

    const body =
      this.bodies.find(
        body =>
          body.plugin?.objectId === objectId
      );


    if (!body) {

      console.warn(
        `Object not found: ${objectId}`
      );

      return;
    }


    const matterVx = this.unitAdapter.velocityMpsToMatter(Number(velocityX));

    Body.setVelocity(
      body,
      {
        x: matterVx,
        y: body.velocity.y
      }
    );
  }


  // =================================
  // GET ENGINE TIME
  // =================================

  getTime() {

    return (
      this.engine.timing.timestamp / 1000
    );
  }


  // =================================
  // TOGGLE WIREFRAMES / COLLIDERS
  // =================================

  setWireframes(enabled) {
    this.render.options.wireframes = Boolean(enabled);
  }

  destroy() {
    this.pause();
    Runner.stop(this.runner);
    Render.stop(this.render);
    Events.off(this.engine);
    Composite.clear(this.engine.world, false);
    if (this.render.canvas) {
      this.render.canvas.remove();
    }
  }
}
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
  createSpringSystem
} from "./physicsBodyFactory.js";


export class Simulation {

  constructor(container) {

    this.container = container;

    // -----------------------------
    // Create Matter.js engine
    // -----------------------------

    this.engine = Engine.create();

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
    // Create runner
    // -----------------------------

    this.runner = Runner.create();


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

  loadScene(scene) {

    this.scene = scene;


    // Clear previous objects

    Composite.clear(
      this.engine.world,
      false
    );


    this.bodies = [];
    this.springSystems = [];


    // -----------------------------
    // Set gravity
    // -----------------------------

    if (scene.environment) {

      this.engine.gravity.y =
        scene.environment.gravity ?? 1;
    }


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

    this.engine.gravity.y =
      Number(value);
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


    Body.setVelocity(
      body,
      {
        x: Number(velocityX),
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
}
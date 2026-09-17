import {
  Bodies,
  Body,
  Constraint
} from "matter-js";

function buildRenderOptions(object, defaultFill = "#3b82f6") {
  const render = {
    visible: object.render?.visible !== false,
  };

  if (object.visual?.sprite_url) {
    render.sprite = {
      texture: object.visual.sprite_url,
      xScale: object.visual.x_scale ?? 1,
      yScale: object.visual.y_scale ?? 1,
    };
  } else if (object.render?.fillStyle || defaultFill) {
    render.fillStyle = object.render?.fillStyle || defaultFill;
  }

  return render;
}

export function createPhysicsBody(object) {

  let body = null;


  // --------------------------------
  // BLOCK
  // --------------------------------

  if (object.type === "block") {

    body = Bodies.rectangle(
      object.initial_position.x,
      object.initial_position.y,
      object.size.width,
      object.size.height,
      {
        isStatic: object.role === "static",
        render: buildRenderOptions(object, "#64748b")
      }
    );
  }


  // --------------------------------
  // CIRCLE
  // --------------------------------

  else if (object.type === "circle") {

    body = Bodies.circle(
      object.initial_position.x,
      object.initial_position.y,
      object.radius,
      {
        isStatic: object.role === "static",
        friction: object.friction ?? 0.08,
        frictionStatic: object.friction_static ?? 0.3,
        restitution: object.restitution ?? 0.05,
        frictionAir: object.friction_air ?? 0.001,
        render: buildRenderOptions(object, "#3b82f6")
      }
    );
  }


  // --------------------------------
  // GROUND
  // --------------------------------

  else if (object.type === "ground") {

    body = Bodies.rectangle(
      object.initial_position.x,
      object.initial_position.y,
      object.size.width,
      object.size.height,
      {
        isStatic: true,
        friction: object.friction ?? 0.1,
        restitution: object.restitution ?? 0.02,
        render: buildRenderOptions(object, "#334155")
      }
    );
  }


  // --------------------------------
  // INCLINED PLANE
  // --------------------------------

  else if (object.type === "inclined_plane") {

    body = Bodies.rectangle(
      object.initial_position.x,
      object.initial_position.y,
      object.size.width,
      object.size.height,
      {
        isStatic: true,
        angle: object.angle * Math.PI / 180,
        friction: object.friction ?? 0.1,
        restitution: object.restitution ?? 0.02,
        render: buildRenderOptions(object, "#475569")
      }
    );
  }


  // --------------------------------
  // POLYGON
  // --------------------------------

  else if (object.type === "polygon") {

    const vertices = object.vertices.map(vertex => ({
      x: vertex.x,
      y: vertex.y
    }));

    body = Bodies.fromVertices(
      object.initial_position.x,
      object.initial_position.y,
      vertices,
      {
        isStatic: object.role === "static",
        friction: object.friction ?? 0.10,
        restitution: object.restitution ?? 0.02,
        render: buildRenderOptions(object, "#1e293b")
      },
      true
    );
  }


  // --------------------------------
  // UNKNOWN OBJECT
  // --------------------------------

  else {

    console.warn(
      `Unknown object type: ${object.type}`
    );

    return null;
  }


  // --------------------------------
  // SET MASS
  // --------------------------------

  if (
    body &&
    object.role === "dynamic" &&
    object.mass_kg
  ) {

    Body.setMass(
      body,
      object.mass_kg
    );
  }


  // --------------------------------
  // SET INITIAL VELOCITY
  // --------------------------------

  if (
    body &&
    object.initial_velocity
  ) {

    Body.setVelocity(
      body,
      {
        x: object.initial_velocity.x,
        y: object.initial_velocity.y
      }
    );
  }


  // Store our JSON object ID
  // inside Matter.js body

  if (body) {

    body.plugin = body.plugin || {};

    body.plugin.objectId = object.id;
  }


  return body;
}


// --------------------------------
// SPRING SYSTEM FACTORY
// --------------------------------

export function createSpringSystem(object) {
  const freePoint = object.free_point;
  const anchorPoint = object.anchor_point;

  // --------------------------
  // Movable collision plate / plunger
  // --------------------------
  const plunger = Bodies.rectangle(
    freePoint.x,
    freePoint.y,
    object.plunger_size?.width ?? 12,
    object.plunger_size?.height ?? 50,
    {
      friction: 0.05,
      restitution: 0.1,
      frictionAir: 0.02,
      render: {
        fillStyle: "#d0a229"
      }
    }
  );

  Body.setMass(plunger, object.plunger_mass ?? 0.5);

  // Prevent plunger from rotating so it acts like a true piston
  Body.setInertia(plunger, Infinity);

  // --------------------------
  // Rest length & Spring constraint
  // --------------------------
  const dx = anchorPoint.x - freePoint.x;
  const dy = anchorPoint.y - freePoint.y;
  const restLength = Math.sqrt(dx * dx + dy * dy);

  const spring = Constraint.create({
    pointA: {
      x: anchorPoint.x,
      y: anchorPoint.y
    },
    bodyB: plunger,
    pointB: {
      x: 0,
      y: 0
    },
    length: restLength,
    stiffness: object.stiffness ?? 0.035,
    damping: object.damping ?? 0.05,
    render: {
      visible: true,
      type: "spring",
      strokeStyle: "#c89c2c",
      lineWidth: 3,
      anchors: false
    }
  });

  if (plunger) {
    plunger.plugin = plunger.plugin || {};
    plunger.plugin.objectId = object.id;
  }

  return {
    id: object.id,
    plunger,
    spring,
    restY: freePoint.y,
    restX: freePoint.x,
    anchorX: anchorPoint.x
  };
}
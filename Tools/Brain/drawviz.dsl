(fn DrawViz ()
  ; toggle the helper meshes from the bools
  (Rendering|SetVisibility :self (Variables|Default|GetFrontArrow) :bNewVisibility (Variables|RobotViz|GetShowFrontArrow) :bPropagateToChildren false)
  (Rendering|SetVisibility :self (Variables|Default|GetSenseRing) :bNewVisibility (Variables|RobotViz|GetShowSenseRange) :bPropagateToChildren false)
  ; the visible body is moved by the Locomotor (gait sway + slope tilt) WITHIN the mesh,
  ; while the helpers are parented to the capsule -> they used to drift apart. Drive the
  ; helpers off the animated `body` bone each tick so they ride with the visible bot.
  (bind bodyLoc (Transformation|GetSocketLocation :self (Variables|Character|GetMesh) :InSocketName "body"))
  (bind fwd (Transformation|GetActorForwardVector self))
  (bind aloc (Transformation|GetActorLocation self))
  ; FrontArrow: sit just above + ahead of the animated body center; it keeps pointing
  ; forward via its capsule-parent rotation, so we only override its world LOCATION.
  (Transformation|SetWorldLocation :self (Variables|Default|GetFrontArrow)
    :NewLocation (+ (+ bodyLoc (Math|Vector|MakeVector 0.0 0.0 22.0)) (* fwd 30.0))
    :bSweep false :bTeleport true)
  ; SenseRing: stays a flat ground ring, but recenters under the body's XY (follows the sway)
  (Transformation|SetWorldLocation :self (Variables|Default|GetSenseRing)
    :NewLocation (Math|Vector|MakeVector (.x bodyLoc) (.y bodyLoc) (- (.z aloc) 59.0))
    :bSweep false :bTeleport true)
  ; scale the sense ring to the current sense radius (cylinder radius 50 -> scale = r/50)
  (bind s (Math|Float|SafeDivide (* (Variables|RobotStats|GetSenseRange) (Variables|RobotStats|GetScrambleFactor)) 50.0))
  (Transformation|SetRelativeScale3D (Variables|Default|GetSenseRing) (Math|Vector|MakeVector s s 0.02)))

(fn SteerAndMove ()
  (bind loc (Transformation|GetActorLocation self))
  ; WANDER: drift a bounded random heading offset each tick -> unpredictable path
  (bind wa0 (+ (Variables|RobotStats|GetWanderAngle) (Math|Random|RandomFloatinRange -4.0 4.0)))
  (bind waC (select (> wa0 70.0) 70.0 (select (< wa0 -70.0) -70.0 wa0)))
  (Variables|RobotStats|SetWanderAngle waC)
  ; seek the goal beacon, rotated by the wander offset, flattened + normalized
  (bind seekRaw (Math|Vector|Normalize2D(Vector) (- (Variables|Default|GetSafeZoneLoc) loc) 0.0001))
  (bind seekN (Math|Vector|Normalize2D(Vector) (Math|Vector|RotateVectorAroundAxis seekRaw (* waC (Variables|RobotStats|GetWanderStrength)) (Math|Vector|MakeVector 0.0 0.0 1.0)) 0.0001))
  (bind inflN (Math|Vector|Normalize2D(Vector) (Variables|Default|GetAccumVec) 0.0001))
  (bind fleeV (select (Variables|Default|GetEvadeFound)
                (* (Math|Vector|Normalize2D(Vector) (Variables|Default|GetEvadeAwayVec) 0.0001) 2.0)
                (Math|Vector|MakeVector 0.0 0.0 0.0)))
  (bind perp (Math|Vector|MakeVector (- (.y seekN)) (.x seekN) 0.0))
  ; sense distance (upgradeable, shrunk by Scramble fields). senseF is FLOAT-ONLY
  ; (used as the SafeDivide divisor); inline a fresh product anywhere it scales a
  ; vector, else the bind gets mis-typed as a vector and the divide won't connect.
  (bind senseF (* (Variables|RobotStats|GetSenseRange) (Variables|RobotStats|GetScrambleFactor)))
  ; WALL whisker -- horizontal trace just above the feet (capsule half-height 59 -> feet at loc.z-59)
  (bind wstart (+ loc (Math|Vector|MakeVector 0.0 0.0 -40.0)))
  (bind (wo wallHit) (Collision|LineTraceByChannel :Start wstart :End (+ wstart (* seekN (* (Variables|RobotStats|GetSenseRange) (Variables|RobotStats|GetScrambleFactor)))) :TraceChannel "TraceTypeQuery1" :bIgnoreSelf true))
  (bind (w1 w2 w3 wdist w5 w6 w7 wIN) (Collision|BreakHitResult wo))
  (bind wallClose (select wallHit (- 1.0 (Math|Float|SafeDivide wdist senseF)) 0.0))
  ; WALL TANGENT: slide along the wall (= a ~90 deg turn on head-on impact).
  ; flatten the wall's impact normal, take both perpendiculars, keep the one that makes progress toward the goal.
  (bind wn (Math|Vector|Normalize2D(Vector) (Math|Vector|MakeVector (.x wIN) (.y wIN) 0.0) 0.0001))
  (bind tA (Math|Vector|MakeVector (- (.y wn)) (.x wn) 0.0))
  (bind tB (Math|Vector|MakeVector (.y wn) (- (.x wn)) 0.0))
  (bind dotA (+ (* (.x seekN) (.x tA)) (* (.y seekN) (.y tA))))
  (bind wallTurn (select (> dotA 0.0) tA tB))
  ; RISE probe: ground stepped up ahead (a ramp) -> treat as obstacle, turn rather than climb
  (bind ahead (+ loc (* seekN (* 0.8 (* (Variables|RobotStats|GetSenseRange) (Variables|RobotStats|GetScrambleFactor))))))
  (bind (ro riseHitB) (Collision|LineTraceByChannel :Start (+ ahead (Math|Vector|MakeVector 0.0 0.0 120.0)) :End (+ ahead (Math|Vector|MakeVector 0.0 0.0 -260.0)) :TraceChannel "TraceTypeQuery1" :bIgnoreSelf true))
  (bind (r1 r2 r3 r4 r5 ript) (Collision|BreakHitResult ro))
  (bind riseW (select (and riseHitB (> (.z ript) (- (.z loc) 14.0))) 1.0 0.0))
  ; how strongly blocked + which way to turn (wall slide, else perpendicular for ramps)
  (bind avoidS (select (> wallClose riseW) wallClose riseW))
  (bind desiredTurn (select wallHit wallTurn perp))
  (bind blocked (> avoidS 0.35))
  ; commit the turn side while blocked (hold -> a clean 90 deg, no flip-flop), clear when free
  (bind oldTurn (Variables|Default|GetTurnDir))
  (bind committed (> (Math|Vector|VectorLength oldTurn) 0.5))
  (bind newTurn (select blocked (select committed oldTurn desiredTurn) (Math|Vector|MakeVector 0.0 0.0 0.0)))
  (Variables|Default|SetTurnDir newTurn)
  ; BLOCKED -> hard turn along the wall (drop the into-wall seek) + a small push off the wall so it doesn't stick.
  ; CLEAR  -> seek the goal. influence + flee always apply.
  (bind moveCore (select blocked (+ newTurn (* wn 0.25)) seekN))
  (bind steer (Math|Vector|Normalize2D(Vector) (+ (+ moveCore inflN) fleeV) 0.0001))
  (Pawn|Input|AddMovementInput :self self :WorldDirection steer :ScaleValue 1.0))

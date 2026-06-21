(fn SteerAndMove ()
  (bind loc (Transformation|GetActorLocation self))
  ; WANDER: drift a bounded random heading offset each tick -> unpredictable path
  (bind wa0 (+ (Variables|RobotStats|GetWanderAngle) (Math|Random|RandomFloatinRange -4.0 4.0)))
  (bind waC (select (> wa0 70.0) 70.0 (select (< wa0 -70.0) -70.0 wa0)))
  (Variables|RobotStats|SetWanderAngle waC)
  ; seek toward the goal beacon, rotated by the wander offset, flattened + normalized
  (bind seekRaw (Math|Vector|Normalize2D(Vector) (- (Variables|Default|GetSafeZoneLoc) loc) 0.0001))
  (bind seekN (Math|Vector|Normalize2D(Vector) (Math|Vector|RotateVectorAroundAxis seekRaw (* waC (Variables|RobotStats|GetWanderStrength)) (Math|Vector|MakeVector 0.0 0.0 1.0)) 0.0001))
  (bind inflN (Math|Vector|Normalize2D(Vector) (Variables|Default|GetAccumVec) 0.0001))
  (bind fleeV (select (Variables|Default|GetEvadeFound)
                (* (Math|Vector|Normalize2D(Vector) (Variables|Default|GetEvadeAwayVec) 0.0001) 2.0)
                (Math|Vector|MakeVector 0.0 0.0 0.0)))
  (bind perp (Math|Vector|MakeVector (- (.y seekN)) (.x seekN) 0.0))
  ; SenseRange (upgradeable) shrunk by ScrambleFactor (Scramble fields) -> sense distance.
  ; senseF is float-only (used as a scalar/divisor); inline a fresh product for the
  ; whisker reach so it isn't mis-typed as a vector.
  (bind senseF (* (Variables|RobotStats|GetSenseRange) (Variables|RobotStats|GetScrambleFactor)))
  ; WALL whisker (distance-weighted -> smooth, no flicker at the edge)
  (bind wstart (+ loc (Math|Vector|MakeVector 0.0 0.0 -78.0)))
  (bind (wo wallHit) (Collision|LineTraceByChannel :Start wstart :End (+ wstart (* seekN (* (Variables|RobotStats|GetSenseRange) (Variables|RobotStats|GetScrambleFactor)))) :TraceChannel "TraceTypeQuery1" :bIgnoreSelf true))
  (bind (w1 w2 w3 wdist w5 w6) (Collision|BreakHitResult wo))
  (bind wallClose (select wallHit (- 1.0 (Math|Float|SafeDivide wdist senseF)) 0.0))
  ; RISE probe: ground stepped up ahead (a ramp) -> treat as obstacle
  (bind ahead (+ loc (* seekN (* 0.8 (* (Variables|RobotStats|GetSenseRange) (Variables|RobotStats|GetScrambleFactor))))))
  (bind (ro riseHitB) (Collision|LineTraceByChannel :Start (+ ahead (Math|Vector|MakeVector 0.0 0.0 120.0)) :End (+ ahead (Math|Vector|MakeVector 0.0 0.0 -260.0)) :TraceChannel "TraceTypeQuery1" :bIgnoreSelf true))
  (bind (r1 r2 r3 r4 r5 ript) (Collision|BreakHitResult ro))
  (bind riseW (select (and riseHitB (> (.z ript) (+ (- (.z loc) 88.0) 45.0))) 1.0 0.0))
  ; combined avoidance strength (whichever is stronger)
  (bind avoidS (select (> wallClose riseW) wallClose riseW))
  (bind blocked (> avoidS 0.08))
  ; commit a turn side while blocked (hold -> no flip-flop), clear when free
  (bind oldTurn (Variables|Default|GetTurnDir))
  (bind committed (> (Math|Vector|VectorLength oldTurn) 0.5))
  (bind newTurn (select blocked (select committed oldTurn perp) (Math|Vector|MakeVector 0.0 0.0 0.0)))
  (Variables|Default|SetTurnDir newTurn)
  ; seek + committed turn scaled by how close the obstacle is + influence/flee
  (bind steer (Math|Vector|Normalize2D(Vector) (+ (+ seekN (* newTurn (* avoidS 2.5))) (+ inflN fleeV)) 0.0001))
  (Pawn|Input|AddMovementInput :self self :WorldDirection steer :ScaleValue 1.0))

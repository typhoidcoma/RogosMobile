(fn RefreshVisuals ()
  ; color by mode: 0 Attract=green, 1 Repel=blue, 2 Evade=red, else (Slow)=yellow
  (bind col (select (== (Variables|Default|GetMode) 0) (Math|Vector|MakeVector 0.1 0.9 0.1)
              (select (== (Variables|Default|GetMode) 1) (Math|Vector|MakeVector 0.1 0.4 1.0)
                (select (== (Variables|Default|GetMode) 2) (Math|Vector|MakeVector 1.0 0.1 0.1)
                  (Math|Vector|MakeVector 1.0 0.85 0.1)))))
  (bind rs (/ (Variables|Default|GetRadius) 50.0))
  ; range sphere: colored + sized to the reaction radius
  (Rendering|Material|SetVectorParameterValueOnMaterials (Variables|Default|GetRangeSphere) (Utilities|Name|MakeLiteralName "Color") col)
  (Transformation|SetRelativeScale3D (Variables|Default|GetRangeSphere) (Math|Vector|MakeVector rs rs rs))
  ; GROUND DISC: same color, flat, sized to the radius, snapped to the floor UNDER the
  ; field so the designer sees the exact ground circle the bot reacts inside (even when
  ; the sphere is placed floating).
  (Rendering|Material|SetVectorParameterValueOnMaterials (Variables|Default|GetGroundDisc) (Utilities|Name|MakeLiteralName "Color") col)
  (Transformation|SetRelativeScale3D (Variables|Default|GetGroundDisc) (Math|Vector|MakeVector rs rs 0.02))
  (bind loc (Transformation|GetActorLocation self))
  (bind (outhit hit) (Collision|LineTraceByChannel :Start loc :End (+ loc (Math|Vector|MakeVector 0.0 0.0 -3000.0)) :TraceChannel "TraceTypeQuery1" :bIgnoreSelf true))
  (bind (h0 h1 h2 h3 h4 himpact) (Collision|BreakHitResult outhit))
  (Transformation|SetWorldLocation :self (Variables|Default|GetGroundDisc)
    :NewLocation (select hit
                   (Math|Vector|MakeVector (.x loc) (.y loc) (+ (.z himpact) 2.0))
                   (Math|Vector|MakeVector (.x loc) (.y loc) (- (.z loc) 50.0)))
    :bSweep false :bTeleport true))

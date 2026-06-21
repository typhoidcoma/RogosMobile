(fn DrawViz ()
  ; toggle the helper meshes from the bools
  (Rendering|SetVisibility :self (Variables|Default|GetFrontArrow) :bNewVisibility (Variables|RobotViz|GetShowFrontArrow) :bPropagateToChildren false)
  (Rendering|SetVisibility :self (Variables|Default|GetSenseRing) :bNewVisibility (Variables|RobotViz|GetShowSenseRange) :bPropagateToChildren false)
  ; scale the sense ring to the current sense radius (cylinder radius 50 -> scale = r/50);
  ; shrinks when scrambled, grows with sensing upgrades
  (bind s (Math|Float|SafeDivide (* (Variables|RobotStats|GetSenseRange) (Variables|RobotStats|GetScrambleFactor)) 50.0))
  (Transformation|SetRelativeScale3D (Variables|Default|GetSenseRing) (Math|Vector|MakeVector s s 0.02)))

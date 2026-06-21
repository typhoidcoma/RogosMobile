(event EventBeginPlay
  (Class|SpringArmComponent|SetTargetArmLength (Variables|Default|GetZoomDistance) (Variables|Default|GetSpringArm))
  (Transformation|SetRelativeRotation (Variables|Default|GetSpringArm) (Math|Rotator|MakeRotator 0.0 -50.0 (Variables|Default|GetOrbitYaw)) false true)
  (bind bot (Actor|GetActorOfClass "/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C"))
  (Variables|Default|SetFollowTarget bot)
  (Utilities|IsValid bot
    (:"Is Valid"
      (Transformation|SetActorLocation self (Transformation|GetActorLocation bot) false true))))

(event EventTick (DeltaSeconds)
  (bind tgt (Variables|Default|GetFollowTarget))
  (Utilities|IsValid tgt
    (:"Is Valid"
      (Transformation|SetActorLocation self
        (Math|Interpolation|VInterpTo (Transformation|GetActorLocation self) (Transformation|GetActorLocation tgt) DeltaSeconds (Variables|Default|GetFollowSpeed)) false true))
    (:"Is Not Valid"
      (Variables|Default|SetFollowTarget (Actor|GetActorOfClass "/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C")))))

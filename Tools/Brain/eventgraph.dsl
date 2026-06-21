(event EventBeginPlay
  (Variables|Default|SetSafeZoneLoc (Transformation|GetActorLocation (Actor|GetActorOfClass "/Game/RogoBot/Gameplay/BP_SafeZone.BP_SafeZone_C")))
  (Class|CharacterMovementComponent|SetMaxWalkSpeed (Variables|RobotStats|GetMoveSpeed) (Variables|Character|GetCharacterMovement)))

(event Collision|EventActorBeginOverlap (OtherActor))

(event EventTick (DeltaSeconds)
  (Variables|RobotStats|SetScrambleFactor 1.0)
  (CallFunction|SenseInfluence)
  (CallFunction|SteerAndMove)
  (CallFunction|DrawViz))

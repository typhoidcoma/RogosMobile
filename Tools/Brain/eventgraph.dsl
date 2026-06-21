(event EventBeginPlay
  (bind _sz (Actor|GetActorOfClass "/Game/RogoBot/Gameplay/BP_SafeZone.BP_SafeZone_C"))
  (Variables|Default|SetSafeZoneLoc (Transformation|GetActorLocation _sz))
  (Class|CharacterMovementComponent|SetMaxWalkSpeed (Variables|RobotStats|GetMoveSpeed) (Variables|Character|GetCharacterMovement)))

(event Collision|EventActorBeginOverlap (OtherActor))

(event EventTick (DeltaSeconds)
  (Variables|RobotStats|SetScrambleFactor 1.0)
  (CallFunction|SenseInfluence)
  ; SenseInfluence (legacy) re-sets MaxWalkSpeed from a HARDCODED 600 every tick, which
  ; overrode MoveSpeed and made the capsule race 4x past the gait (SpeedMax 160) -> skating
  ; + the rig trailing. Re-assert the real MoveSpeed (x the influence SpeedMult) right after.
  (Class|CharacterMovementComponent|SetMaxWalkSpeed (* (Variables|RobotStats|GetMoveSpeed) (Variables|Default|GetSpeedMult)) (Variables|Character|GetCharacterMovement))
  (CallFunction|SteerAndMove)
  (CallFunction|DrawViz))

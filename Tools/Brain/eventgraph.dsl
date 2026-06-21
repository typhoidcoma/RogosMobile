(event EventBeginPlay
  (Variables|Default|SetSafeZoneLoc (Transformation|GetActorLocation (Actor|GetActorOfClass "/Game/RogoBot/Gameplay/BP_SafeZone.BP_SafeZone_C"))))

(event Collision|EventActorBeginOverlap (OtherActor))

(event EventTick (DeltaSeconds)
  (CallFunction|SenseInfluence)
  (CallFunction|SteerAndMove))

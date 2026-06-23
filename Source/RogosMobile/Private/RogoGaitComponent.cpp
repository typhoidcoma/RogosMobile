#include "RogoGaitComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Actor.h"
#include "Kismet/KismetSystemLibrary.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Character.h"
#include "Components/CapsuleComponent.h"

URogoGaitComponent::URogoGaitComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PrePhysics;   // run before the mesh's anim eval

	// Defaults for the RogoBot skeleton: diagonal trot.
	HipBones = { TEXT("hip_FL"), TEXT("hip_FR"), TEXT("hip_BL"), TEXT("hip_BR") };
	PhaseOffsets = { 0.f, 0.5f, 0.5f, 0.f };
}

void URogoGaitComponent::BeginPlay()
{
	Super::BeginPlay();
	SampleRestLayout();
}

void URogoGaitComponent::SampleRestLayout()
{
	const AActor* Owner = GetOwner();
	if (Owner == nullptr)
	{
		return;
	}
	const USkeletalMeshComponent* Mesh = Owner->FindComponentByClass<USkeletalMeshComponent>();
	if (Mesh == nullptr)
	{
		return;
	}

	const FTransform ActorXf = Owner->GetActorTransform();
	const int32 NumLegs = HipBones.Num();
	if (NumLegs == 0)
	{
		return;
	}

	// At BeginPlay the mesh may not be posed yet -> GetBoneLocation returns ~origin, giving
	// garbage actor-local offsets. Validate every hip sits within a sane radius of the actor;
	// if not, stay uninitialised and retry on a later tick.
	TArray<FVector> Sampled;
	Sampled.SetNum(NumLegs);
	for (int32 i = 0; i < NumLegs; ++i)
	{
		const FVector HipWorld = Mesh->GetBoneLocation(HipBones[i], EBoneSpaces::WorldSpace);
		const FVector Local = ActorXf.InverseTransformPosition(HipWorld);
		if (Local.SizeSquared() > FMath::Square(300.f))   // > 3 m from the pawn -> not posed yet
		{
			return;
		}
		Sampled[i] = Local;
	}

	HipRestOffsets = Sampled;
	if (BodyBone != NAME_None)
	{
		BodyRestOffset = ActorXf.InverseTransformPosition(Mesh->GetBoneLocation(BodyBone, EBoneSpaces::WorldSpace));
	}
	bInitialised = true;
}

void URogoGaitComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	const AActor* Owner = GetOwner();
	if (Owner == nullptr)
	{
		return;
	}
	if (!bInitialised)
	{
		SampleRestLayout();
		if (!bInitialised)
		{
			return;
		}
	}

	const int32 NumLegs = HipRestOffsets.Num();
	const FTransform ActorXf = Owner->GetActorTransform();

	// Velocity -> planar move direction + speed.
	const FVector Velocity = Owner->GetVelocity();
	FVector Move(Velocity.X, Velocity.Y, 0.f);
	const float Speed = Move.Size();
	if (!Move.Normalize())
	{
		Move = ActorXf.GetUnitAxis(EAxis::X);   // idle -> face forward
	}

	// Body-dynamics spring: lean from momentum (inertial lag) + banking into turns. The Sway
	// (pitch,roll) is integrated here and folded into BodyUpWorld below (after the slope tilt).
	if (bBodyDynamics && DeltaTime > KINDA_SMALL_NUMBER)
	{
		// Drive the lean from the STEERING INPUT (clean intent) + speed, not noisy measured
		// derivatives (those saturate/ring on this jittery AI). Bounded to [-1,1] so it can't
		// blow up. Lean forward into the run (+ extra when braking) and bank into the steer dir.
		FVector InDir = FVector::ZeroVector;
		if (const UCharacterMovementComponent* CMC = Owner->FindComponentByClass<UCharacterMovementComponent>())
		{
			const FVector IA = CMC->GetCurrentAcceleration();
			InDir = FVector(IA.X, IA.Y, 0.f).GetSafeNormal();
		}
		const FVector Fwd = ActorXf.GetUnitAxis(EAxis::X);
		const FVector Right = ActorXf.GetUnitAxis(EAxis::Y);
		const float SpeedFrac = FMath::Min(Speed / 150.f, 1.f);
		const float Longi = SpeedFrac - 0.6f * FMath::Max(0.f, -FVector::DotProduct(InDir, Fwd));  // run-lean + brake
		const float Latrl = FVector::DotProduct(InDir, Right);                                     // steer left/right

		const float LP = FMath::Clamp(DeltaTime * DynSmoothRate, 0.f, 1.f);
		SmoothFwdAccel = FMath::Lerp(SmoothFwdAccel, Longi, LP);
		SmoothTurn = FMath::Lerp(SmoothTurn, Latrl, LP);

		// Gate off when nearly stopped (a near-stationary AI jitters its input/velocity).
		const float SpeedGate = FMath::Clamp((Speed - 25.f) / 35.f, 0.f, 1.f);
		const FVector2D Target(
			FMath::Clamp(AccelSwayGain * SmoothFwdAccel, -SwayMaxDeg, SwayMaxDeg) * SpeedGate,   // pitch: lean into run
			FMath::Clamp(TurnSwayGain * SmoothTurn, -SwayMaxDeg, SwayMaxDeg) * SpeedGate);        // roll: bank into steer

		const FVector2D SpringAcc = (Target - Sway) * SwayStiffness - SwayVel * SwayDamping;
		SwayVel += SpringAcc * DeltaTime;
		Sway += SwayVel * DeltaTime;
		Sway.X = FMath::Clamp(Sway.X, -SwayMaxDeg, SwayMaxDeg);
		Sway.Y = FMath::Clamp(Sway.Y, -SwayMaxDeg, SwayMaxDeg);
	}
	else
	{
		Sway = FVector2D::ZeroVector;
		SwayVel = FVector2D::ZeroVector;
		bDynInit = false;
	}

	// Cadence scales with speed (state persists fine here), phase integrated from DeltaTime.
	const float Freq = FMath::Max(Frequency + CadenceGain * Speed, KINDA_SMALL_NUMBER);
	Phase = FMath::Frac(Phase + DeltaTime * Freq);

	const float Stride = Speed / Freq;
	const float Stance = FMath::Clamp(StanceFraction, 0.05f, 0.95f);
	const float Amp = Stance * Stride * 0.5f;

	// Self-tuning: derive effective step-height + crouch from speed and the terrain measured
	// last tick (Grade/Roughness). Faster/rougher -> higher steps; steeper -> deeper crouch.
	float EffStepHeight = StepHeight;
	float EffCrouch = BodyHeightOffset;
	if (bSelfTune)
	{
		EffStepHeight = StepHeight + StepHeightSpeedGain * Speed + StepHeightRoughGain * Roughness;
		EffStepHeight = FMath::Clamp(EffStepHeight, StepHeight, StepHeight * 3.f + 40.f);
		// Deeper crouch on steeper grade, clamped so the legs can't fully collapse.
		EffCrouch = BodyHeightOffset - FMath::Min(CrouchGradeGain * Grade, 30.f);
	}

	if (PlantAnchors.Num() != NumLegs) { PlantAnchors.SetNum(NumLegs); }
	if (PrevLegPhase.Num() != NumLegs) { PrevLegPhase.SetNumZeroed(NumLegs); }
	FeetTargetsWorld.SetNum(NumLegs);
	TArray<FVector> FootGround;            // per-foot ground point (no lift) for the slope plane
	FootGround.SetNum(NumLegs);

	// Ground probe under a foot XY: surface Z + whether it's a usable foothold (hit + not too
	// steep). Same trace channel as the steering probes; ignores self.
	UWorld* World = GetWorld();
	AActor* OwnerNC = GetOwner();
	const float FootWalkableZ = FMath::Cos(FMath::DegreesToRadians(FMath::Clamp(FootMaxAngleDeg, 5.f, 89.f)));
	struct FGroundProbe { bool bValid; float Z; };
	auto Probe = [&](float X, float Y, float FlatZ) -> FGroundProbe
	{
		if (!bGroundTrace || World == nullptr) { return { true, FlatZ }; }   // trace off -> flat is fine
		const FVector Start(X, Y, FlatZ + GroundTraceUp);
		const FVector End(X, Y, FlatZ - GroundTraceDown);
		FHitResult Hit;
		TArray<AActor*> Ignore;
		if (OwnerNC) { Ignore.Add(OwnerNC); }
		if (UKismetSystemLibrary::LineTraceSingle(World, Start, End, ETraceTypeQuery::TraceTypeQuery1,
			false, Ignore, EDrawDebugTrace::None, Hit, true))
		{
			// Valid foothold = hit, not too steep, AND within leg reach (not a far-below ledge drop).
			const bool bOk = (Hit.ImpactNormal.Z >= FootWalkableZ)
				&& (Hit.Location.Z >= FlatZ - MaxFootReachDrop);
			return { bOk, (float)(Hit.Location.Z + FootGroundOffset) };
		}
		return { false, FlatZ };   // miss = gap/cliff -> not a foothold
	};

	// Find solid ground for a foot: try the desired spot, else pull inward toward the hip.
	// bOutSupported = whether real ground was found (false = floating, fed to the balance check).
	auto FindFoothold = [&](const FVector& Desired, const FVector& Hip, bool& bOutSupported) -> FVector
	{
		const FGroundProbe d = Probe(Desired.X, Desired.Y, Hip.Z);
		if (!bFootholdCheck || d.bValid) { bOutSupported = d.bValid; return FVector(Desired.X, Desired.Y, d.Z); }
		for (float Pull = 0.34f; Pull <= 1.001f; Pull += 0.33f)   // 0.34, 0.67, 1.0 toward the hip
		{
			const float X = FMath::Lerp(Desired.X, Hip.X, Pull);
			const float Y = FMath::Lerp(Desired.Y, Hip.Y, Pull);
			const FGroundProbe p = Probe(X, Y, Hip.Z);
			if (p.bValid) { bOutSupported = true; return FVector(X, Y, p.Z); }
		}
		bOutSupported = false;
		return FVector(Hip.X, Hip.Y, Hip.Z);   // nothing solid -> least-bad: under the hip, flat height
	};

	int32 NumSup = 0;
	FVector2D SupSum(0.f, 0.f);   // sum of supported feet XY -> support centroid for the balance check

	for (int32 i = 0; i < NumLegs; ++i)
	{
		// Splay the footprint outward (crab stance) by scaling the hip's lateral+longitudinal
		// offset in actor-local space before going to world.
		FVector LocalHip = HipRestOffsets[i];
		LocalHip.X *= StanceScale;
		LocalHip.Y *= StanceScale;
		FVector Home = ActorXf.TransformPosition(LocalHip);
		Home.Z -= RestDrop;

		const float Off = PhaseOffsets.IsValidIndex(i) ? PhaseOffsets[i] : 0.f;
		const float LegPhase = FMath::Frac(Phase + Off);
		const bool bStance = LegPhase < Stance;

		// Next plant: under the hip, led forward by Amp, on a validated foothold (gaps/edges/
		// too-steep spots are pulled in toward the hip until solid ground is found).
		bool bSupported = false;
		const FVector Landing = FindFoothold(Home + Move * Amp, Home, bSupported);
		if (bSupported) { ++NumSup; SupSum += FVector2D(Landing.X, Landing.Y); }

		// Touchdown = swing->stance transition (phase wrapped past 1.0 into [0,Stance)).
		const bool bJustLanded = (PrevLegPhase[i] >= Stance) && bStance;
		if (bJustLanded || PlantAnchors[i].IsNearlyZero())
		{
			PlantAnchors[i] = Landing;   // capture the solid spot, held through stance
		}

		FVector Foot;
		float SurfaceZ;
		if (bStance)
		{
			Foot = PlantAnchors[i];     // held world anchor (incl. terrain Z) -> turn-proof + grounded
			SurfaceZ = Foot.Z;
		}
		else
		{
			const float s = (LegPhase - Stance) / (1.f - Stance);
			const FVector LiftOff = PlantAnchors[i];
			Foot.X = FMath::Lerp(LiftOff.X, Landing.X, s);
			Foot.Y = FMath::Lerp(LiftOff.Y, Landing.Y, s);
			SurfaceZ = FMath::Lerp(LiftOff.Z, Landing.Z, s);          // arc base follows the ground
			const float StepUp = FMath::Max(0.f, Landing.Z - LiftOff.Z);
			const float Arc = EffStepHeight + StepOverGain * StepUp;  // clear a ledge edge
			Foot.Z = SurfaceZ + FMath::Sin(s * PI) * Arc;
		}

		FeetTargetsWorld[i] = FTransform(Foot);
		FootGround[i] = FVector(Foot.X, Foot.Y, SurfaceZ);
		PrevLegPhase[i] = LegPhase;
	}

	// Topple to ragdoll ONLY when the body tips too far over: measure the LEAN of the body off its
	// support base -- the angle from vertical of the line from the support centroid (feet on real
	// ground) up to the body. Balanced/upright (incl. walkable slopes, where the feet still sit
	// under the body) -> small angle. Perched half off a ledge so the body hangs past its feet ->
	// large angle -> tip over. Must exceed BalanceMargin (DEGREES) for BalanceGrace before it falls.
	SupportedFeet = NumSup;
	if (bBalanceTopple && NumLegs >= 4)
	{
		bool bTipped = false;
		if (NumSup > 0)
		{
			const FVector AL = ActorXf.GetLocation();
			const FVector2D Centroid = SupSum / (float)NumSup;
			const float LeanDist = FVector2D(AL.X - Centroid.X, AL.Y - Centroid.Y).Size();
			const float BodyH = FMath::Max(20.f, RestDrop);   // body sits ~RestDrop above the feet
			const float TipDeg = FMath::RadiansToDegrees(FMath::Atan2(LeanDist, BodyH));
			bTipped = TipDeg > BalanceMargin;   // BalanceMargin reused as the tip angle in degrees
		}
		UnbalanceTime = bTipped ? (UnbalanceTime + DeltaTime) : FMath::Max(0.f, UnbalanceTime - DeltaTime * 2.f);
		if (UnbalanceTime > BalanceGrace)
		{
			UnbalanceTime = 0.f;
			SetRagdoll(true);   // tipped past the threshold -> fall over
			return;
		}
	}

	// Body height: speed/terrain-tuned crouch (EffCrouch) lowers the body so legs fold (spider)
	// plus the per-cycle bob that dips at the two stance midpoints (diagonal trot).
	BodyBobZ = EffCrouch - BodyBob * (0.5f - 0.5f * FMath::Cos(Phase * 2.f * PI * 2.f));

	// Plane through the four grounded feet -> normal N. Drives both the body tilt (slope
	// follow) and the terrain metrics (grade + roughness) that feed the self-tuning above.
	BodyUpWorld = FVector::UpVector;
	if (NumLegs >= 4)
	{
		// FL=0 FR=1 BL=2 BR=3.
		const FVector Front = (FootGround[0] + FootGround[1]) * 0.5f;
		const FVector Back  = (FootGround[2] + FootGround[3]) * 0.5f;
		const FVector Lft   = (FootGround[0] + FootGround[2]) * 0.5f;
		const FVector Rgt   = (FootGround[1] + FootGround[3]) * 0.5f;
		FVector N = FVector::CrossProduct(Rgt - Lft, Front - Back);   // plane normal
		if (N.Z < 0.f) { N = -N; }
		if (N.Normalize())
		{
			// Terrain metrics (smoothed): grade = how far the plane tilts from flat;
			// roughness = RMS of the feet off that plane (bumpiness).
			const FVector Centroid = (FootGround[0] + FootGround[1] + FootGround[2] + FootGround[3]) * 0.25f;
			float SumSq = 0.f;
			for (int32 k = 0; k < 4; ++k)
			{
				const float d = FVector::DotProduct(FootGround[k] - Centroid, N);
				SumSq += d * d;
			}
			const float RawRough = FMath::Sqrt(SumSq * 0.25f);
			const float RawGrade = 1.f - N.Z;
			const float A = FMath::Clamp(DeltaTime * TerrainSmoothRate, 0.f, 1.f);
			Grade = FMath::Lerp(Grade, RawGrade, A);
			Roughness = FMath::Lerp(Roughness, RawRough, A);

			if (bBodyTilt)
			{
				const float Ang = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(N.Z, -1.f, 1.f)));
				const float t = FMath::Clamp(BodyTiltStrength, 0.f, 1.f)
					* FMath::Min(1.f, BodyTiltMaxDeg / FMath::Max(Ang, KINDA_SMALL_NUMBER));
				BodyUpWorld = FMath::Lerp(FVector::UpVector, N, t).GetSafeNormal();
			}
		}
	}

	// Fold the momentum-sway lean into the body up-vector (on top of the slope tilt): pitch
	// around the movement-right axis, roll/bank around the movement axis.
	if (bBodyDynamics && (FMath::Abs(Sway.X) > 0.01f || FMath::Abs(Sway.Y) > 0.01f))
	{
		const FVector RightAxis = FVector::CrossProduct(Move, FVector::UpVector).GetSafeNormal();
		const FQuat Q = FQuat(RightAxis, FMath::DegreesToRadians(Sway.X))
			* FQuat(Move, FMath::DegreesToRadians(Sway.Y));
		BodyUpWorld = Q.RotateVector(BodyUpWorld).GetSafeNormal();
	}
}

void URogoGaitComponent::AddBodyImpulse(FVector WorldDir, float Strength)
{
	const AActor* Owner = GetOwner();
	if (Owner == nullptr) { return; }
	FVector D(WorldDir.X, WorldDir.Y, 0.f);
	if (!D.Normalize()) { return; }
	const FTransform X = Owner->GetActorTransform();
	const float F = FVector::DotProduct(D, X.GetUnitAxis(EAxis::X));   // +front .. -back of the shove
	const float R = FVector::DotProduct(D, X.GetUnitAxis(EAxis::Y));   // +right .. -left
	// The body's top lags AWAY from the shove direction, then the spring settles it back.
	SwayVel.X += -F * Strength;
	SwayVel.Y += -R * Strength;
}

void URogoGaitComponent::Knockback(FVector WorldDir, float Speed)
{
	if (ACharacter* Ch = Cast<ACharacter>(GetOwner()))
	{
		Ch->LaunchCharacter(WorldDir.GetSafeNormal() * Speed, true, false);   // override planar velocity
	}
	AddBodyImpulse(WorldDir, Speed * 0.3f);   // body lurches with the shove
}

void URogoGaitComponent::SetRagdoll(bool bOn)
{
	AActor* Owner = GetOwner();
	if (Owner == nullptr) { return; }
	USkeletalMeshComponent* Mesh = Owner->FindComponentByClass<USkeletalMeshComponent>();
	UCharacterMovementComponent* CMC = Owner->FindComponentByClass<UCharacterMovementComponent>();
	ACharacter* Ch = Cast<ACharacter>(Owner);

	if (bOn)
	{
		// Stop the capsule/movement and the gait so they don't fight the simulated mesh.
		if (CMC) { CMC->StopMovementImmediately(); CMC->DisableMovement(); }
		if (Ch && Ch->GetCapsuleComponent()) { Ch->GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryOnly); }
		SetComponentTickEnabled(false);
		if (Mesh)
		{
			// Keep the existing (non-self-colliding) profile: the auto-generated per-bone bodies
			// overlap, so enabling body-vs-body collision (the "Ragdoll" profile) explodes them.
			Mesh->SetEnableGravity(true);                            // ragdoll needs gravity
			Mesh->SetAllBodiesPhysicsBlendWeight(1.f);
			Mesh->SetAllPhysicsLinearVelocity(FVector::ZeroVector);   // drop any inherited velocity
			Mesh->SetAllBodiesSimulatePhysics(true);
			Mesh->SetSimulatePhysics(true);                          // whole mesh incl. root -> full tumble
			Mesh->WakeAllRigidBodies();
		}
	}
	else
	{
		// Best-effort recovery: stop simulating, re-enable movement + the gait.
		const float HH = (Ch && Ch->GetCapsuleComponent()) ? Ch->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 59.f;
		if (Mesh)
		{
			Mesh->SetSimulatePhysics(false);
			Mesh->SetCollisionProfileName(TEXT("PhysicsActor"));
			Mesh->AttachToComponent(Ch ? (USceneComponent*)Ch->GetCapsuleComponent() : Owner->GetRootComponent(),
				FAttachmentTransformRules::SnapToTargetNotIncludingScale);
			Mesh->SetRelativeLocationAndRotation(FVector(0.f, 0.f, -HH), FRotator(0.f, -90.f, 0.f));
		}
		if (Ch && Ch->GetCapsuleComponent()) { Ch->GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics); }
		if (CMC) { CMC->SetMovementMode(MOVE_Walking); }
		bInitialised = false;   // re-sample the rest layout
		SetComponentTickEnabled(true);
	}
}

void URogoGaitComponent::Die()
{
	SetRagdoll(true);
}

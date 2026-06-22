#include "RogoGaitComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Actor.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Engine/SkeletalMesh.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "Rendering/SkeletalMeshLODRenderData.h"
#include "Rendering/SkinWeightVertexBuffer.h"

URogoGaitComponent::URogoGaitComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PrePhysics;   // run before the mesh's anim eval

	// Defaults for the RogoBot skeleton: diagonal trot.
	HipBones = { TEXT("hip_FL"), TEXT("hip_FR"), TEXT("hip_BL"), TEXT("hip_BR") };
	PhaseOffsets = { 0.f, 0.5f, 0.5f, 0.f };

	// Debug per-leg colors (FL red, FR green, BL blue, BR yellow).
	LegColors = {
		FLinearColor(1.f, 0.05f, 0.05f, 1.f),
		FLinearColor(0.05f, 1.f, 0.05f, 1.f),
		FLinearColor(0.1f, 0.3f, 1.f, 1.f),
		FLinearColor(1.f, 0.9f, 0.05f, 1.f)
	};
}

void URogoGaitComponent::BeginPlay()
{
	Super::BeginPlay();
	SampleRestLayout();
	if (bDebugLegColors)
	{
		ApplyLegDebugColors();
	}
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

	// Ground Z under a foot XY (the real surface, for slopes). Falls back to the flat foot
	// height when disabled or nothing is hit. Same trace channel as the steering probes.
	UWorld* World = GetWorld();
	AActor* OwnerNC = GetOwner();
	auto GroundZ = [&](const FVector& AtXY, float FlatZ) -> float
	{
		if (!bGroundTrace || World == nullptr) { return FlatZ; }
		const FVector Start(AtXY.X, AtXY.Y, FlatZ + GroundTraceUp);
		const FVector End(AtXY.X, AtXY.Y, FlatZ - GroundTraceDown);
		FHitResult Hit;
		TArray<AActor*> Ignore;
		if (OwnerNC) { Ignore.Add(OwnerNC); }
		const bool bHit = UKismetSystemLibrary::LineTraceSingle(
			World, Start, End, ETraceTypeQuery::TraceTypeQuery1, false, Ignore,
			EDrawDebugTrace::None, Hit, true);
		return bHit ? Hit.Location.Z + FootGroundOffset : FlatZ;
	};

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

		// Next plant: under the hip, led forward by Amp; Z snapped onto the ground there.
		FVector PlantTarget = Home + Move * Amp;
		PlantTarget.Z = GroundZ(PlantTarget, Home.Z);

		// Touchdown = swing->stance transition (phase wrapped past 1.0 into [0,Stance)).
		const bool bJustLanded = (PrevLegPhase[i] >= Stance) && bStance;
		if (bJustLanded || PlantAnchors[i].IsNearlyZero())
		{
			PlantAnchors[i] = PlantTarget;   // capture world spot + its ground height, held through stance
		}

		FVector Foot;
		float SurfaceZ;
		if (bStance)
		{
			Foot = PlantAnchors[i];     // held world anchor (incl. slope Z) -> turn-proof + grounded
			SurfaceZ = Foot.Z;
		}
		else
		{
			const float s = (LegPhase - Stance) / (1.f - Stance);
			Foot = FMath::Lerp(PlantAnchors[i], PlantTarget, s);
			SurfaceZ = GroundZ(Foot, Home.Z);
			Foot.Z = SurfaceZ + FMath::Sin(s * PI) * EffStepHeight;   // arc above the surface
		}

		FeetTargetsWorld[i] = FTransform(Foot);
		FootGround[i] = FVector(Foot.X, Foot.Y, SurfaceZ);
		PrevLegPhase[i] = LegPhase;
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
}

void URogoGaitComponent::ApplyLegDebugColors()
{
	AActor* Owner = GetOwner();
	if (Owner == nullptr) { return; }
	USkeletalMeshComponent* Mesh = Owner->FindComponentByClass<USkeletalMeshComponent>();
	if (Mesh == nullptr) { return; }
	USkeletalMesh* Asset = Mesh->GetSkeletalMeshAsset();
	if (Asset == nullptr) { return; }
	FSkeletalMeshRenderData* RD = Asset->GetResourceForRendering();
	if (RD == nullptr || RD->LODRenderData.Num() == 0) { return; }

	FSkeletalMeshLODRenderData& LOD = RD->LODRenderData[0];
	const FSkinWeightVertexBuffer* SWB = LOD.GetSkinWeightVertexBuffer();
	const int32 NumVerts = LOD.GetNumVertices();
	if (SWB == nullptr || NumVerts == 0) { return; }
	const FReferenceSkeleton& RefSkel = Asset->GetRefSkeleton();
	const int32 MaxInf = (int32)SWB->GetMaxBoneInfluences();

	auto LegFromBone = [](const FName& Bone) -> int32
	{
		const FString S = Bone.ToString();
		if (S.EndsWith(TEXT("_FL"))) { return 0; }
		if (S.EndsWith(TEXT("_FR"))) { return 1; }
		if (S.EndsWith(TEXT("_BL"))) { return 2; }
		if (S.EndsWith(TEXT("_BR"))) { return 3; }
		return INDEX_NONE;
	};

	TArray<FColor> Colors;
	Colors.Init(BodyColor.ToFColor(false), NumVerts);

	for (const FSkelMeshRenderSection& Section : LOD.RenderSections)
	{
		for (uint32 v = 0; v < Section.NumVertices; ++v)
		{
			const int32 GlobalV = Section.BaseVertexIndex + v;

			// Dominant influence for this vertex.
			int32 BestInf = 0;
			uint16 BestW = 0;
			for (int32 inf = 0; inf < MaxInf; ++inf)
			{
				const uint16 W = SWB->GetBoneWeight(GlobalV, inf);
				if (W > BestW) { BestW = W; BestInf = inf; }
			}
			const int32 LocalBone = SWB->GetBoneIndex(GlobalV, BestInf);
			if (!Section.BoneMap.IsValidIndex(LocalBone)) { continue; }
			const FName BoneName = RefSkel.GetBoneName(Section.BoneMap[LocalBone]);

			const int32 Leg = LegFromBone(BoneName);
			if (Leg != INDEX_NONE && LegColors.IsValidIndex(Leg))
			{
				Colors[GlobalV] = LegColors[Leg].ToFColor(false);
			}
		}
	}

	CachedSlot0Material = Mesh->GetMaterial(0);
	Mesh->SetVertexColorOverride(0, Colors);
	if (DebugMaterial)
	{
		Mesh->SetMaterial(0, DebugMaterial);
	}
}

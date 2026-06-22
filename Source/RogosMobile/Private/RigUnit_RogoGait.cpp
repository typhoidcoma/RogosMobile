#include "RigUnit_RogoGait.h"
#include "Units/RigUnitContext.h"
#include "Rigs/RigHierarchy.h"
#include "Components/SceneComponent.h"
#include "GameFramework/Actor.h"

FRigUnit_RogoGait_Execute()
{
	DECLARE_SCOPE_HIERARCHICAL_COUNTER_RIGUNIT()

	URigHierarchy* Hierarchy = ExecuteContext.Hierarchy;
	if (Hierarchy == nullptr)
	{
		return;
	}

	const int32 NumLegs = Hips.Num();
	if (NumLegs == 0)
	{
		return;
	}

	// Gait phase from the rig's absolute time (stateless -> no reliance on instance
	// state persistence). Cadence (Frequency) is the driver of the leg cycle.
	const float Phase = FMath::Frac(ExecuteContext.GetAbsoluteTime() * Frequency);

	// Read the body's actual velocity from the owning actor (the BP drives the capsule
	// at Frequency*stride). Direction + speed both come from here -> no BP->CR plumbing.
	FVector Velocity = FVector::ZeroVector;
	if (const USceneComponent* OwningComp = ExecuteContext.GetOwningComponent())
	{
		if (const AActor* Owner = OwningComp->GetOwner())
		{
			Velocity = Owner->GetVelocity();
		}
	}
	FVector Move(Velocity.X, Velocity.Y, 0.f);
	const float Speed = Move.Size();
	if (!Move.Normalize())
	{
		Move = FVector::ForwardVector;
	}

	const float Freq = FMath::Max(Frequency, KINDA_SMALL_NUMBER);
	const float Stride = Speed / Freq;                          // distance travelled per cycle
	const float Stance = FMath::Clamp(StanceFraction, 0.05f, 0.95f);
	// Body-local along-move amplitude that keeps a planted foot world-fixed: the foot
	// slides backward by (Stance * Stride) over the stance phase = body advance over stance.
	const float Amp = Stance * Stride * 0.5f;

	FeetTransforms.SetNum(NumLegs);
	for (int32 i = 0; i < NumLegs; ++i)
	{
		const FTransform HipT = Hierarchy->GetGlobalTransform(Hips[i]);
		FVector Home = HipT.GetLocation();
		Home.Z -= RestDrop;                                     // rest foot sits below the hip

		const float Off = PhaseOffsets.IsValidIndex(i) ? PhaseOffsets[i] : 0.f;
		const float LegPhase = FMath::Frac(Phase + Off);

		float Along;
		float Lift = 0.f;
		if (LegPhase < Stance)
		{
			// Stance: world-locked — body-local offset slides +Amp -> -Amp.
			const float s = LegPhase / Stance;                  // 0..1
			Along = Amp * (1.f - 2.f * s);
		}
		else
		{
			// Swing: reach back forward -Amp -> +Amp with a sine lift arc.
			const float s = (LegPhase - Stance) / (1.f - Stance); // 0..1
			Along = Amp * (2.f * s - 1.f);
			Lift = FMath::Sin(s * PI) * StepHeight;
		}

		FVector FootPos = Home + Move * Along;
		FootPos.Z += Lift;
		FeetTransforms[i] = FTransform(FootPos);
	}

	// Body bob: dips at each of the two stance midpoints per cycle (diagonal trot).
	const float BobZ = -BodyBob * (0.5f - 0.5f * FMath::Cos(Phase * 2.f * PI * 2.f));
	if (BodyBone.IsValid())
	{
		BodyTransform = Hierarchy->GetGlobalTransform(BodyBone);
		BodyTransform.AddToTranslation(FVector(0.f, 0.f, BobZ));
	}
}

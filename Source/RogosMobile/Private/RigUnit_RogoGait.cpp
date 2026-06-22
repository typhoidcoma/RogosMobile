#include "RigUnit_RogoGait.h"
#include "RogoGaitComponent.h"
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

	// Owning skeletal mesh component (rig "global" space == this component's space) + owner.
	const USceneComponent* OwningComp = ExecuteContext.GetOwningComponent();
	const AActor* Owner = OwningComp ? OwningComp->GetOwner() : nullptr;
	const URogoGaitComponent* Gait = Owner ? Owner->FindComponentByClass<URogoGaitComponent>() : nullptr;

	// Body: current global pose + the component's bob Z (0 if no component).
	if (BodyBone.IsValid())
	{
		BodyTransform = Hierarchy->GetGlobalTransform(BodyBone);
		const float BobZ = Gait ? Gait->BodyBobZ : 0.f;
		BodyTransform.AddToTranslation(FVector(0.f, 0.f, BobZ));

		// Tilt the body to follow the slope: rotate so the rig's up aligns with the gait's
		// slope up-vector (computed from the grounded feet). Flat ground -> no tilt.
		if (Gait && OwningComp && Gait->bBodyTilt)
		{
			const FVector UpComp = OwningComp->GetComponentTransform()
				.InverseTransformVectorNoScale(Gait->BodyUpWorld).GetSafeNormal();
			if (!UpComp.IsNearlyZero())
			{
				const FQuat Tilt = FQuat::FindBetweenNormals(FVector::UpVector, UpComp);
				BodyTransform.SetRotation(Tilt * BodyTransform.GetRotation());
			}
		}
	}

	if (Gait && OwningComp && Gait->FeetTargetsWorld.Num() > 0)
	{
		// Convert the component's WORLD foot targets into rig (component) space.
		const FTransform CompXf = OwningComp->GetComponentTransform();
		const int32 NumLegs = Gait->FeetTargetsWorld.Num();
		FeetTransforms.SetNum(NumLegs);
		for (int32 i = 0; i < NumLegs; ++i)
		{
			FeetTransforms[i] = Gait->FeetTargetsWorld[i].GetRelativeTransform(CompXf);
		}
		return;
	}

	// --- Fallback: no component -> rest the feet under their hips so the rig still poses. ---
	const int32 NumLegs = Hips.Num();
	FeetTransforms.SetNum(NumLegs);
	for (int32 i = 0; i < NumLegs; ++i)
	{
		FTransform HipT = Hierarchy->GetGlobalTransform(Hips[i]);
		FVector Foot = HipT.GetLocation();
		Foot.Z -= RestDrop;
		FeetTransforms[i] = FTransform(Foot);
	}
}

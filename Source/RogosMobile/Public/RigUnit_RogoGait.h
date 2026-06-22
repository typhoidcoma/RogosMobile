#pragma once

#include "CoreMinimal.h"
#include "Units/RigUnit.h"
#include "RigUnit_RogoGait.generated.h"

/**
 * Thin IK-target provider for the RogoBot gait. The real (stateful) gait runs on the pawn
 * in URogoGaitComponent — which can hold per-tick state, unlike this AnimBP-hosted Control
 * Rig. This unit just reads that component off the owning actor, converts its WORLD-space
 * foot targets into rig (component) space, and applies the body-bob Z. Output feet ->
 * 4x TwoBoneIK; output body -> SetTransform(body).
 *
 * Fallback (no component found): feet rest under their hips (RestDrop below), body unbobbed,
 * so the rig still poses sanely.
 */
USTRUCT(meta = (DisplayName = "Rogo Gait", Category = "RogoBot", NodeColor = "0.1 0.5 0.1"))
struct ROGOSMOBILE_API FRigUnit_RogoGait : public FRigUnitMutable
{
	GENERATED_BODY()

	RIGVM_METHOD()
	virtual void Execute() override;

	/** Hip bones, one per leg, in the component's leg order (for the no-component fallback
	 *  and to size the output). */
	UPROPERTY(meta = (Input))
	TArray<FRigElementKey> Hips;

	/** Distance the resting foot sits below its hip (cm) — used by the fallback. */
	UPROPERTY(meta = (Input))
	float RestDrop = 53.f;

	/** Body bone the bob is applied to. */
	UPROPERTY(meta = (Input))
	FRigElementKey BodyBone;

	/** World-space foot targets, one per leg (feed each to a TwoBoneIK effector). */
	UPROPERTY(meta = (Output))
	TArray<FTransform> FeetTransforms;

	/** Body bone target (current pose + vertical bob). */
	UPROPERTY(meta = (Output))
	FTransform BodyTransform;
};

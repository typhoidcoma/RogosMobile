#pragma once

#include "CoreMinimal.h"
#include "Units/RigUnit.h"
#include "RigUnit_RogoGait.generated.h"

/**
 * RogoBot self-driven quadruped gait (leg-driven motion).
 *
 * A phase timer advances at `Frequency` (the leg cadence). Each leg, offset by its
 * `PhaseOffsets` entry, alternates stance (planted) and swing (lift + reach ahead).
 * During stance the foot's body-local offset slides backward at exactly the body speed,
 * so the planted foot stays world-fixed while the body advances over it -> the legs
 * visibly drive the motion ("fake root motion": equivalent look to true root motion,
 * which UE 5.8 can't do from a Control Rig).
 *
 * FULLY STATELESS by necessity: this AnimBP-hosted Control Rig re-initialises its rig
 * instance whenever the hierarchy is mutated, and RigVM WorkData does not persist across
 * ticks — so neither an integrated (speed-scaled) cadence nor per-leg world-locked plant
 * anchors are possible (any control write mid-solve freezes AbsoluteTime). Everything is
 * therefore derived from the current frame: phase from absolute time, foot offset from a
 * closed-form world-lock that is exact for straight motion (feet slide some in turns).
 *
 * Outputs world-space foot targets (-> 4x TwoBoneIK) and a bobbed body transform.
 */
USTRUCT(meta = (DisplayName = "Rogo Gait", Category = "RogoBot", NodeColor = "0.1 0.5 0.1"))
struct ROGOSMOBILE_API FRigUnit_RogoGait : public FRigUnitMutable
{
	GENERATED_BODY()

	RIGVM_METHOD()
	virtual void Execute() override;

	// Move direction + Speed are read at runtime from the owning actor's velocity
	// (ExecuteContext.GetOwningComponent()->GetOwner()->GetVelocity()), so no BP->CR
	// pin wiring is needed.

	/** Gait cadence (cycles/sec) — the leg step frequency. */
	UPROPERTY(meta = (Input))
	float Frequency = 1.5f;

	/** Fraction of a cycle a foot is planted (0..1). */
	UPROPERTY(meta = (Input))
	float StanceFraction = 0.6f;

	/** Peak swing-foot lift (cm). */
	UPROPERTY(meta = (Input))
	float StepHeight = 14.f;

	/** Body vertical bob amplitude (cm). */
	UPROPERTY(meta = (Input))
	float BodyBob = 6.f;

	/** Distance the resting foot sits below its hip (cm) — flat-ground foot height. */
	UPROPERTY(meta = (Input))
	float RestDrop = 56.f;

	/** Hip bones, one per leg, in the same order as PhaseOffsets / output FeetTransforms. */
	UPROPERTY(meta = (Input))
	TArray<FRigElementKey> Hips;

	/** Per-leg phase offset (0..1). Diagonal trot = {0, 0.5, 0.5, 0}. */
	UPROPERTY(meta = (Input))
	TArray<float> PhaseOffsets;

	/** Body bone to bob. */
	UPROPERTY(meta = (Input))
	FRigElementKey BodyBone;

	/** World-space foot targets, one per leg (feed each to a TwoBoneIK effector). */
	UPROPERTY(meta = (Output))
	TArray<FTransform> FeetTransforms;

	/** Body bone target (current pose + vertical bob). */
	UPROPERTY(meta = (Output))
	FTransform BodyTransform;
};

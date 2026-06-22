#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RogoGaitComponent.generated.h"

/**
 * Stateful quadruped gait, computed on the pawn (where per-tick state actually persists,
 * unlike the AnimBP-hosted Control Rig). Each tick it advances a phase, and per leg holds
 * a WORLD-space plant anchor captured at touchdown -> the planted foot stays world-fixed
 * even while the body turns (turn-proof, no foot-slide). Cadence scales with speed.
 *
 * Outputs world-space foot targets + a body transform; the thin `FRigUnit_RogoGait` reads
 * this component off the owner and converts them to rig space for IK. Targets are derived
 * from the ACTOR transform + velocity (not live bone poses), so this is independent of the
 * anim/CR evaluation order.
 */
UCLASS(ClassGroup = (RogoBot), meta = (BlueprintSpawnableComponent))
class ROGOSMOBILE_API URogoGaitComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	URogoGaitComponent();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	/** Base cadence at zero speed (cycles/sec). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float Frequency = 1.5f;

	/** Cadence added per cm/s of speed -> faster = quicker steps AND longer (bounded) strides. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float CadenceGain = 0.01f;

	/** Fraction of a cycle a foot is planted (0..1). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float StanceFraction = 0.6f;

	/** Peak swing-foot lift (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float StepHeight = 14.f;

	/** Body vertical bob amplitude (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float BodyBob = 6.f;

	/** Distance the resting foot sits below its hip (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float RestDrop = 53.f;

	/** Splays the planted footprint outward from the body centerline (1 = under the hips,
	 *  >1 = wider crab stance). Scales each foot's lateral+longitudinal offset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float StanceScale = 1.5f;

	/** Hip bones, one per leg (FL, FR, BL, BR). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	TArray<FName> HipBones;

	/** Per-leg phase offset (0..1). Diagonal trot = {0, 0.5, 0.5, 0}. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	TArray<float> PhaseOffsets;

	/** Body bone (for the bob reference height). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	FName BodyBone = TEXT("body");

	// --- Debug: per-leg vertex coloring (testing aid) ---

	/** When true, at BeginPlay paint each leg's vertices a distinct color (by dominant bone)
	 *  and swap the mesh to DebugMaterial so the colors show. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Debug")
	bool bDebugLegColors = false;

	/** Per-leg debug colors, same order as HipBones (FL, FR, BL, BR). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Debug")
	TArray<FLinearColor> LegColors;

	/** Color for body / non-leg vertices. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Debug")
	FLinearColor BodyColor = FLinearColor(0.15f, 0.15f, 0.15f, 1.f);

	/** Material that displays vertex color (M_LegDebug). Swapped onto slot 0 while debugging. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Debug")
	TObjectPtr<UMaterialInterface> DebugMaterial = nullptr;

	/** WORLD-space foot targets, one per leg (read by FRigUnit_RogoGait). */
	UPROPERTY(BlueprintReadOnly, Category = "RogoGait")
	TArray<FTransform> FeetTargetsWorld;

	/** Current vertical body-bob offset (cm). The rig adds this to the body bone's Z;
	 *  vertical so world Z == component Z (mesh is only yawed). */
	UPROPERTY(BlueprintReadOnly, Category = "RogoGait")
	float BodyBobZ = 0.f;

private:
	float Phase = 0.f;
	bool bInitialised = false;

	// Per-leg state (world space) + the rest layout sampled once from the mesh ref pose.
	TArray<FVector> PlantAnchors;     // world plant point held through stance
	TArray<float> PrevLegPhase;       // for swing->stance touchdown detection
	TArray<FVector> HipRestOffsets;   // hip location in actor-local space
	FVector BodyRestOffset = FVector::ZeroVector;

	/** Sample hip/body rest offsets in actor-local space from the skeletal mesh. */
	void SampleRestLayout();

	/** Paint per-leg vertex colors (by dominant bone) + swap to DebugMaterial. */
	void ApplyLegDebugColors();

	/** Original slot-0 material, cached so debug coloring can be reverted. */
	TObjectPtr<UMaterialInterface> CachedSlot0Material = nullptr;
};

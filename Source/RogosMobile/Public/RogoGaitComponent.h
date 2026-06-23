#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RogoGaitComponent.generated.h"

class UPhysicalAnimationComponent;

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

	/** Kick the body-sway spring so it recoils from a hit coming along WorldDir (the body's top
	 *  lags away from the shove, then settles). Strength is roughly the angular kick (deg/s). */
	UFUNCTION(BlueprintCallable, Category = "RogoGait|Dynamics")
	void AddBodyImpulse(FVector WorldDir, float Strength);

	/** Shove the whole pawn: launch the capsule along WorldDir at Speed (cm/s) AND lurch the body
	 *  (knockback). The capsule's velocity change also feeds the momentum sway. */
	UFUNCTION(BlueprintCallable, Category = "RogoGait|Dynamics")
	void Knockback(FVector WorldDir, float Speed);

	/** Collapse into / out of a physics ragdoll. On: stop movement, disable the gait, simulate the
	 *  mesh from its current pose. Off: best-effort return to the walking state. */
	UFUNCTION(BlueprintCallable, Category = "RogoGait|Dynamics")
	void SetRagdoll(bool bOn);

	/** Convenience: collapse into a ragdoll (= SetRagdoll(true)). Wire this to your death event. */
	UFUNCTION(BlueprintCallable, Category = "RogoGait|Dynamics")
	void Die();

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

	/** Constant vertical offset applied to the body (cm). Negative = crouch: lowers the body
	 *  so the legs fold and the knees rise (spider posture); feet stay grounded. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float BodyHeightOffset = -15.f;

	/** Distance the resting foot sits below its hip (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float RestDrop = 53.f;

	/** Splays the planted footprint outward from the body centerline (1 = under the hips,
	 *  >1 = wider crab stance). Scales each foot's lateral+longitudinal offset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait")
	float StanceScale = 1.5f;

	// --- Ground tracing: plant feet on the real surface (slopes/ramps) instead of a flat Z. ---

	/** Trace each foot down onto the ground so it follows terrain. Off = flat-ground gait. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	bool bGroundTrace = true;

	/** How far above the flat foot height the ground trace starts (cm). Keep modest: too high
	 *  over-grabs onto overhead ledges on cluttered geometry. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	float GroundTraceUp = 30.f;

	/** How far below the flat foot height the ground trace reaches (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	float GroundTraceDown = 80.f;

	/** Lift planted feet this far off the traced surface (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	float FootGroundOffset = 0.f;

	/** Validate footholds: if a foot would land on a gap, edge, cliff, or too-steep face,
	 *  pull it inward toward the hip to find solid ground instead. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	bool bFootholdCheck = true;

	/** Steepest surface (deg) still accepted as a foothold; steeper = rejected, foot pulls in. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	float FootMaxAngleDeg = 50.f;

	/** Extra swing lift per cm of step-up height, so the foot clears a ledge edge and lands
	 *  on top (reach onto steps). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	float StepOverGain = 0.6f;

	/** A foothold more than this far BELOW the foot's rest height is out of leg reach (a ledge
	 *  drop / cliff) -> rejected, so the foot gathers onto solid ground instead of stretching. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	float MaxFootReachDrop = 40.f;

	// --- Balance: topple into a ragdoll when the body overhangs unsupported ground. ---

	/** When too few feet support the body and its center hangs past them, ragdoll off the edge. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Balance")
	bool bBalanceTopple = true;

	/** Tip-over angle (DEGREES): how far the body may lean off its support base before it topples. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Balance")
	float BalanceMargin = 55.f;

	/** Seconds the body must stay unbalanced before it topples (debounce vs momentary gaps). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Balance")
	float BalanceGrace = 0.4f;

	/** Feet that found real support this tick (read-only). */
	UPROPERTY(BlueprintReadOnly, Category = "RogoGait|Balance")
	int32 SupportedFeet = 0;

	// --- Physical parts: per-bone bodies simulate toward the gait pose so they collide/deflect. ---

	/** Drive the body+legs as simulated physics bodies motored toward the gait pose (real
	 *  per-part collision). Off = pure kinematic mesh. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|PhysParts")
	bool bPhysicalParts = true;

	/** Bone at/below which the bodies simulate (root stays kinematic, anchored to the capsule). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|PhysParts")
	FName PhysSimRootBone = TEXT("body");

	/** Motor stiffness pulling each body's orientation to the animated pose (higher = stiffer
	 *  follow, less deflection). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|PhysParts")
	float PhysAnimStrength = 1500.f;

	/** Motor damping on angular velocity error (higher = calmer). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|PhysParts")
	float PhysAnimDamping = 80.f;

	/** Clamp on the motor's angular force (0 = unlimited). Lower lets hard collisions overpower
	 *  the motor and deflect the limbs. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|PhysParts")
	float PhysAnimMaxForce = 0.f;

	/** Tilt the body to match the slope under the feet (pitch/roll), so it leans into hills
	 *  instead of staying flat. Also equalises leg reach on grades. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	bool bBodyTilt = true;

	/** How fully the body aligns to the slope (0 = upright, 1 = full slope match). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	float BodyTiltStrength = 0.9f;

	/** Max body tilt from vertical (deg) — clamp so steep ground can't over-rotate the rig. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Ground")
	float BodyTiltMaxDeg = 40.f;

	/** World-space body up-vector the rig tilts the body bone toward (slope-follow). */
	UPROPERTY(BlueprintReadOnly, Category = "RogoGait")
	FVector BodyUpWorld = FVector::UpVector;

	// --- Self-tuning: gait adapts to speed + terrain (no manual tuning per situation). ---

	/** Master toggle for the speed/terrain adaptation below. Off = use the base values as-is. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|SelfTune")
	bool bSelfTune = true;

	/** Added foot-lift per cm/s of speed (cm). Faster = higher steps. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|SelfTune")
	float StepHeightSpeedGain = 0.06f;

	/** Added foot-lift per cm of terrain roughness. Bumpier ground = higher steps to clear it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|SelfTune")
	float StepHeightRoughGain = 1.5f;

	/** Extra crouch (cm) per unit of grade (grade = 1-cos(slope); ~0.13 at 30deg, 0.29 at 45deg).
	 *  Steeper = lower body. Clamped so it can't fully collapse the legs. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|SelfTune")
	float CrouchGradeGain = 50.f;

	/** How fast the measured grade/roughness follow the terrain (per sec). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|SelfTune")
	float TerrainSmoothRate = 4.f;

	/** Measured terrain grade under the feet (0 flat .. ~0.3 at 45deg). Read-only. */
	UPROPERTY(BlueprintReadOnly, Category = "RogoGait|SelfTune")
	float Grade = 0.f;

	/** Measured terrain roughness under the feet (RMS off the foot plane, cm). Read-only. */
	UPROPERTY(BlueprintReadOnly, Category = "RogoGait|SelfTune")
	float Roughness = 0.f;

	// --- Physics-reactive: a procedural spring leans the body from momentum/impacts. ---

	/** Master toggle for the momentum sway / impact lean. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Dynamics")
	bool bBodyDynamics = true;

	/** Forward lean (deg) at full speed — the body leans into its run (driven by the steering
	 *  input, not noisy measured accel), with extra forward lean when braking. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Dynamics")
	float AccelSwayGain = 8.f;

	/** Bank (deg) at full steer — leans into the steering direction. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Dynamics")
	float TurnSwayGain = 12.f;

	/** Spring stiffness pulling the lean toward its target (higher = snappier). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Dynamics")
	float SwayStiffness = 40.f;

	/** Spring damping (~critical for the stiffness above = no wobble). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Dynamics")
	float SwayDamping = 13.f;

	/** Max lean from any one axis (deg). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Dynamics")
	float SwayMaxDeg = 14.f;

	/** Low-pass rate (per sec) for the steering-input lean signal before the spring.
	 *  Lower = smoother but laggier. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "RogoGait|Dynamics")
	float DynSmoothRate = 4.f;

	/** Current sway lean (X = pitch fwd/back, Y = roll/bank), deg. Read-only. */
	UPROPERTY(BlueprintReadOnly, Category = "RogoGait|Dynamics")
	FVector2D Sway = FVector2D::ZeroVector;

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

	// Body-dynamics spring state.
	FVector2D SwayVel = FVector2D::ZeroVector;   // d(Sway)/dt for the pitch/roll spring
	FVector PrevVelocity = FVector::ZeroVector;
	float PrevYaw = 0.f;
	float SmoothFwdAccel = 0.f;                  // low-passed body-frame accel + turn rate
	float SmoothTurn = 0.f;
	bool bDynInit = false;
	float UnbalanceTime = 0.f;                   // how long the body has overhung unsupported ground

	TObjectPtr<UPhysicalAnimationComponent> PhysAnim = nullptr;   // motors the simulated bodies
	bool bPhysSetup = false;

	/** One-time physical-animation setup (sim the body+legs, motor them to the pose). */
	void SetupPhysicalParts();

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

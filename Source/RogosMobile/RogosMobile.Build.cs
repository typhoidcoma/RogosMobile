using UnrealBuildTool;

public class RogosMobile : ModuleRules
{
	public RogosMobile(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		// ControlRig + RigVM: needed to define a custom RigUnit (FRigUnit / RIGVM_METHOD).
		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core", "CoreUObject", "Engine", "ControlRig", "RigVM"
		});
	}
}

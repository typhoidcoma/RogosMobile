using UnrealBuildTool;

public class RogosMobileTarget : TargetRules
{
	public RogosMobileTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V7;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("RogosMobile");
	}
}

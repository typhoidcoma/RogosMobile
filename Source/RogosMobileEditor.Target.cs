using UnrealBuildTool;

public class RogosMobileEditorTarget : TargetRules
{
	public RogosMobileEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V7;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("RogosMobile");
	}
}

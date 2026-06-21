import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
print("in_pie:", les.is_in_play_in_editor())
# find the PIE world + bot
ws = unreal.EditorLevelLibrary.get_game_world() if hasattr(unreal.EditorLevelLibrary,"get_game_world") else None
bot = None
for w in unreal.GameplayStatics.get_all_actors_of_class(ws, unreal.load_class(None,"/Game/RogoBot/Character/BP_RogoBot.BP_RogoBot_C")) if ws else []:
    bot = w; break
if not bot:
    # fallback: scan all worlds
    for actor in unreal.EditorActorSubsystem().get_all_level_actors():
        if "RogoBot" in actor.get_class().get_name():
            bot = actor; break
if not bot:
    print("BOT NOT FOUND");
else:
    loc = bot.get_actor_location()
    mesh = bot.get_component_by_class(unreal.SkeletalMeshComponent)
    vel = bot.get_velocity()
    spd = (vel.x**2+vel.y**2+vel.z**2)**0.5
    print("BOT loc:", round(loc.x,1), round(loc.y,1), round(loc.z,1), "speed=", round(spd,1))
    zs = {}
    for b in ["body","ankle_FL","ankle_FR","ankle_BL","ankle_BR"]:
        t = mesh.get_socket_transform(b, unreal.RelativeTransformSpace.RTS_WORLD)
        zs[b] = round(t.translation.z,2)
    print("  ankle z  FL=%s FR=%s BL=%s BR=%s  body=%s" %
          (zs["ankle_FL"],zs["ankle_FR"],zs["ankle_BL"],zs["ankle_BR"],zs["body"]))

from engines.luraph_v15    import run as luraph_v15_run
from engines.luraph_v14    import run as luraph_v14_run
from engines.ironbrew2     import run as ironbrew2_run
from engines.ironbrew1     import run as ironbrew1_run
from engines.moonsec       import run as moonsec_run
from engines.fuscator77    import run as fuscator77_run
from engines.prometheus    import run as prometheus_run
from engines.clyde         import run as clyde_run
from engines.luaobfuscator import run as luaobfuscator_run
from engines.ironveil      import run as ironveil_run
from engines.hercules      import run as hercules_run
from engines.centurion     import run as centurion_run
from engines.luast         import run as luast_run
from engines.flowauth      import run as flowauth_run

_REGISTRY = {
    "luraph_v15":    luraph_v15_run,
    "luraph_v14":    luraph_v14_run,
    "ironbrew2":     ironbrew2_run,
    "ironbrew1":     ironbrew1_run,
    "moonsec":       moonsec_run,
    "77fuscator":    fuscator77_run,
    "prometheus":    prometheus_run,
    "clyde":         clyde_run,
    "luaobfuscator": luaobfuscator_run,
    "ironveil":      ironveil_run,
    "hercules":      hercules_run,
    "centurion":     centurion_run,
    "luast":         luast_run,
    "flowauth":      flowauth_run,
}


def get_engine(name: str):
    return _REGISTRY.get(name.lower())


def list_engines():
    return list(_REGISTRY.keys())

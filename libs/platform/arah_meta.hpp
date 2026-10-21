#pragma once

#include "platform/servers_list.hpp"

namespace arah
{
// Drops metaserver settings Arah must not take from CoMaps' metaserver (its donate link).
downloader::MetaConfig::SettingsMap FilterMetaSettings(downloader::MetaConfig::SettingsMap settings);
}  // namespace arah

#include "platform/arah_meta.hpp"

#include "platform/arah_config.hpp"
#include "platform/settings.hpp"

#include <string>

namespace arah
{
downloader::MetaConfig::SettingsMap FilterMetaSettings(downloader::MetaConfig::SettingsMap settings)
{
  if (!kAcceptMetaserverDonateUrl)
    settings.erase(std::string(settings::kDonateUrl));
  return settings;
}
}  // namespace arah

#include "testing/testing.hpp"

#include "platform/arah_meta.hpp"
#include "platform/platform.hpp"
#include "platform/servers_list.hpp"

namespace arah_config_tests
{
// CoMaps' metaserver still supplies Arah's download servers until Arah hosts its own (spec §5 placeholder),
// but its donate link must not reach Arah's settings.
UNIT_TEST(Arah_MetaserverDonateIgnored)
{
  auto const config = downloader::ParseMetaConfig(
      R"({"servers":["https://a.example/"],"settings":{"DonateUrl":"https://comaps.app/donate/","NY":"1"}})");
  TEST(config, ());
  TEST_EQUAL(config->m_serversList, (downloader::MetaConfig::ServersList{"https://a.example/"}), ());
  auto const kept = arah::FilterMetaSettings(config->m_settings);
  TEST_EQUAL(kept.count("DonateUrl"), 0, ());
  TEST_EQUAL(kept.count("NY"), 1, ());
}

UNIT_TEST(Arah_DefaultServersStillParse)
{
  auto const config = downloader::ParseMetaConfig(GetPlatform().DefaultUrlsJSON());
  TEST(config, ());
  TEST(!config->m_serversList.empty(), ());
}
}  // namespace arah_config_tests

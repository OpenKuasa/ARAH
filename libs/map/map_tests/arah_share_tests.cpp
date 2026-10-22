#include "testing/testing.hpp"

#include "map/arah_share.hpp"

#include "base/string_utils.hpp"

#include <string>

namespace arah_share_tests
{
// With no Arah domain, a shared place carries its name, details, coordinates and a standard map link.
UNIT_TEST(Arah_ShareTextHasNoCoMapsLink)
{
  std::string const text = arah::ShareText("Masjid Jamek", "Jalan Tun Perak, Kuala Lumpur", 3.14893, 101.69585, 17);
  TEST(text.find("Masjid Jamek") != std::string::npos, (text));
  TEST(text.find("Jalan Tun Perak, Kuala Lumpur") != std::string::npos, (text));
  TEST(text.find("3.14893, 101.69585") != std::string::npos, (text));
  TEST(text.find("https://www.openstreetmap.org/?mlat=3.14893&mlon=101.69585#map=17/3.14893/101.69585") !=
           std::string::npos,
       (text));
  std::string lower = text;
  strings::AsciiToLower(lower);
  for (char const * brand : {"comaps", "omaps", "ge0"})
    TEST(lower.find(brand) == std::string::npos, (brand, text));
}

UNIT_TEST(Arah_ShareTextSkipsEmptyDetails)
{
  std::string const text = arah::ShareText("Masjid Jamek", "", 3.14893, 101.69585, 17);
  TEST(text.find("\n\n") == std::string::npos, (text));
  TEST_EQUAL(text.find("Masjid Jamek\n3.14893, 101.69585\n"), 0, (text));
}

UNIT_TEST(Arah_ShareLinkRoundsAndKeepsSign)
{
  TEST_EQUAL(arah::ShareLink(-6.2000049, -0.5, 12),
             "https://www.openstreetmap.org/?mlat=-6.20000&mlon=-0.50000#map=12/-6.20000/-0.50000", ());
}
}  // namespace arah_share_tests

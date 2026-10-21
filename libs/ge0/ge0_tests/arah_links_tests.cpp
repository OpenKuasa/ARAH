#include "testing/testing.hpp"

#include "ge0/parser.hpp"

#include <string>

namespace arah_links_tests
{
// Places shared from CoMaps (or older apps) must still open in Arah.
UNIT_TEST(Arah_OldLinksStillParse)
{
  for (std::string const url : {"https://comaps.at/Byqqqqqqqq/Name", "cm://Byqqqqqqqq/Name", "comaps://Byqqqqqqqq/Name",
                                "ge0://Byqqqqqqqq/Name"})
  {
    ge0::Ge0Parser parser;
    ge0::Ge0Parser::Result result;
    TEST(parser.Parse(url, result), (url));
    TEST_ALMOST_EQUAL_ABS(result.m_lat, 45.0, 1e-5, (url));
    TEST_ALMOST_EQUAL_ABS(result.m_lon, 0.0, 1e-5, (url));
    TEST_EQUAL(result.m_name, "Name", (url));
  }
}
}  // namespace arah_links_tests

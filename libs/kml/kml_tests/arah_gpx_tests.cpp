#include "testing/testing.hpp"

#include "kml/serdes_gpx.hpp"
#include "kml/types.hpp"

#include "coding/writer.hpp"

#include <string>

namespace arah_gpx_tests
{
// Exported GPX files name Arah as their creator.
UNIT_TEST(Arah_GpxCreatorIsArah)
{
  kml::FileData const data;
  std::string buffer;
  MemWriter<decltype(buffer)> sink(buffer);
  kml::gpx::SerializerGpx(data).Serialize(sink);

  TEST(buffer.find(R"(creator="Arah")") != std::string::npos, (buffer));
  TEST_EQUAL(buffer.find("CoMaps"), std::string::npos, (buffer));
}
}  // namespace arah_gpx_tests

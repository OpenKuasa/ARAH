#include "map/arah_share.hpp"

#include <cstdio>

namespace arah
{
namespace
{
std::string Coordinate(double value)
{
  char buf[32];
  std::snprintf(buf, sizeof(buf), "%.5f", value);
  return buf;
}
}  // namespace

std::string ShareLink(double lat, double lon, int zoom)
{
  std::string const la = Coordinate(lat);
  std::string const lo = Coordinate(lon);
  return "https://www.openstreetmap.org/?mlat=" + la + "&mlon=" + lo + "#map=" + std::to_string(zoom) + "/" + la + "/" +
         lo;
}

std::string ShareText(std::string_view name, std::string_view details, double lat, double lon, int zoom)
{
  std::string text;
  for (std::string_view line : {name, details})
    if (!line.empty())
      text.append(line).push_back('\n');
  text += Coordinate(lat) + ", " + Coordinate(lon) + "\n" + ShareLink(lat, lon, zoom);
  return text;
}
}  // namespace arah

#pragma once

#include <string>
#include <string_view>

namespace arah
{
// Arah has no domain for share links yet (arah::kShareLinkBase), so places are shared as OpenStreetMap links.
// https://www.openstreetmap.org/?mlat=<lat>&mlon=<lon>#map=<zoom>/<lat>/<lon>, coordinates to 5 decimals.
std::string ShareLink(double lat, double lon, int zoom);

// "<name>\n<details>\n<lat>, <lon>\n<ShareLink>", skipping an empty name or details line.
std::string ShareText(std::string_view name, std::string_view details, double lat, double lon, int zoom);
}  // namespace arah

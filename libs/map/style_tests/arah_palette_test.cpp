#include "testing/testing.hpp"

#include "map/style_tests/helpers.hpp"

#include "indexer/classificator.hpp"
#include "indexer/drawing_rules.hpp"
#include "indexer/drules_include.hpp"
#include "indexer/feature_data.hpp"
#include "indexer/feature_visibility.hpp"
#include "indexer/map_style.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <optional>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace arah_palette_test
{
// Colors are stored with an inverted alpha, so opaque colors read as 0x00RRGGBB.
uint32_t constexpr kRouteLight = 0x0F8B7E;
uint32_t constexpr kRouteDark = 0x3DCFB6;
uint32_t constexpr kBackgroundLight = 0xF4F1EA;
uint32_t constexpr kBackgroundDark = 0x1B2023;

// Upstream traffic colors, identical in every style family. Traffic carries meaning, so Arah keeps them.
// G3 has `-opacity: 0.0` upstream, which the generator encodes as an inverted alpha byte of 0xFF.
struct TrafficColor
{
  std::string_view m_name;
  uint32_t m_light;
  uint32_t m_dark;
};

constexpr std::array<TrafficColor, 10> kTrafficColors = {{
    {"TrafficG0", 0x7E1712, 0x4C120F},
    {"TrafficG1", 0xE42300, 0x731816},
    {"TrafficG2", 0xE42300, 0x731816},
    {"TrafficG3", 0xFFFCDE00, 0xFF8C7012},
    {"TrafficG4", 0x39962E, 0x376222},
    {"TrafficG5", 0x39962E, 0x376222},
    {"RouteTrafficG0", 0x9B2300, 0x5E0F0D},
    {"RouteTrafficG1", 0xE82705, 0x7F1311},
    {"RouteTrafficG2", 0xE82705, 0x7F1311},
    {"RouteTrafficG3", 0xFFFFE500, 0xFF9E8216},
}};

// Pins Arah's Tenang palette so an upstream merge can't silently revert it.
// Every CoMaps map mode (walking, cycling, driving, public transport, outdoors) imports the default palette.
UNIT_TEST(Arah_TenangPalette)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    auto const & rules = drule::rules();
    bool const isDark = MapStyleIsDark(mapStyle);
    TEST_EQUAL(rules.GetColor("Route"), isDark ? kRouteDark : kRouteLight, (mapStyle));
    TEST_EQUAL(rules.GetBgColor(17), isDark ? kBackgroundDark : kBackgroundLight, (mapStyle));
  });
}

UNIT_TEST(Arah_TrafficColorsUnchanged)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    auto const & rules = drule::rules();
    bool const isDark = MapStyleIsDark(mapStyle);
    for (auto const & t : kTrafficColors)
      TEST_EQUAL(rules.GetColor(std::string(t.m_name)), isDark ? t.m_dark : t.m_light, (mapStyle, t.m_name));
  });
}

double Luminance(uint32_t rgb)
{
  auto const channel = [](uint32_t c)
  {
    double const v = c / 255.0;
    return v <= 0.03928 ? v / 12.92 : std::pow((v + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * channel((rgb >> 16) & 0xFF) + 0.7152 * channel((rgb >> 8) & 0xFF) + 0.0722 * channel(rgb & 0xFF);
}

// WCAG contrast ratio, 1..21.
double Contrast(uint32_t a, uint32_t b)
{
  double const la = Luminance(a);
  double const lb = Luminance(b);
  return (std::max(la, lb) + 0.05) / (std::min(la, lb) + 0.05);
}

// HSV hue in degrees, 0..360.
double Hue(uint32_t rgb)
{
  double const r = ((rgb >> 16) & 0xFF) / 255.0;
  double const g = ((rgb >> 8) & 0xFF) / 255.0;
  double const b = (rgb & 0xFF) / 255.0;
  double const maxC = std::max({r, g, b});
  double const delta = maxC - std::min({r, g, b});
  if (delta == 0)
    return 0;
  double h;
  if (maxC == r)
    h = std::fmod((g - b) / delta, 6.0);
  else if (maxC == g)
    h = (b - r) / delta + 2;
  else
    h = (r - g) / delta + 4;
  h *= 60;
  return h < 0 ? h + 360 : h;
}

double HueDistance(uint32_t a, uint32_t b)
{
  double const d = std::fabs(Hue(a) - Hue(b));
  return std::min(d, 360 - d);
}

// Blends a stored color (inverted alpha in the top byte) over an opaque background.
uint32_t BlendOver(uint32_t color, uint32_t bg)
{
  double const alpha = 1.0 - ((color >> 24) & 0xFF) / 255.0;
  uint32_t out = 0;
  for (int shift = 0; shift <= 16; shift += 8)
  {
    double const c = ((color >> shift) & 0xFF) * alpha + ((bg >> shift) & 0xFF) * (1.0 - alpha);
    out |= static_cast<uint32_t>(std::lround(c)) << shift;
  }
  return out;
}

drule::KeysT GetKeys(std::vector<std::string_view> const & path, feature::GeomType geomType, int scale)
{
  feature::TypesHolder holder(geomType);
  holder.Add(classif().GetTypeByPath(path));
  drule::KeysT keys;
  feature::GetDrawRule(holder, scale, keys);
  return keys;
}

// On-map color of the top line (the fill, not the casing) of a line type at a scale.
std::optional<uint32_t> LineFillColor(std::vector<std::string_view> const & path, int scale)
{
  auto const & rules = drule::rules();
  LineRuleProto const * top = nullptr;
  for (auto const & key : GetKeys(path, feature::GeomType::Line, scale))
  {
    if (key.m_type != drule::line)
      continue;
    auto const * line = rules.Find(key)->GetLine();
    if (line && (!top || line->priority() > top->priority()))
      top = line;
  }
  if (!top)
    return {};
  return BlendOver(top->color(), rules.GetBgColor(scale) & 0xFFFFFF);
}

// On-map color of the topmost fill of an area type at a scale.
std::optional<uint32_t> AreaFillColor(std::vector<std::string_view> const & path, int scale)
{
  auto const & rules = drule::rules();
  AreaRuleProto const * top = nullptr;
  for (auto const & key : GetKeys(path, feature::GeomType::Area, scale))
  {
    if (key.m_type != drule::area)
      continue;
    auto const * area = rules.Find(key)->GetArea();
    if (area && (!top || area->priority() > top->priority()))
      top = area;
  }
  if (!top)
    return {};
  return BlendOver(top->color(), rules.GetBgColor(scale) & 0xFFFFFF);
}

// Stored (inverted alpha) primary caption text color of an area type at a scale.
std::optional<uint32_t> AreaCaptionColor(std::vector<std::string_view> const & path, int scale)
{
  auto const & rules = drule::rules();
  for (auto const & key : GetKeys(path, feature::GeomType::Area, scale))
  {
    if (key.m_type != drule::caption)
      continue;
    auto const * caption = rules.Find(key)->GetCaption();
    if (caption && caption->has_primary())
      return caption->primary().color();
  }
  return {};
}

// Stored (inverted alpha) primary text color of a line type's name at a scale.
std::optional<uint32_t> LineTextColor(std::vector<std::string_view> const & path, int scale)
{
  auto const & rules = drule::rules();
  for (auto const & key : GetKeys(path, feature::GeomType::Line, scale))
  {
    if (key.m_type != drule::pathtext)
      continue;
    auto const * text = rules.Find(key)->GetPathtext();
    if (text && text->has_primary())
      return text->primary().color();
  }
  return {};
}

bool IsArahNightStyle(MapStyle mapStyle)
{
  return mapStyle == MapStyleDefaultDark || mapStyle == MapStyleVehicleDark;
}

// Secondary roads must stand out from the beige and from white minor streets (a driving app needs the hierarchy).
UNIT_TEST(Arah_LightSecondaryRoadsVisible)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    if (mapStyle != MapStyleDefaultLight && mapStyle != MapStyleVehicleLight)
      return;
    auto const & rules = drule::rules();
    for (int scale : {12, 15})
    {
      auto const secondary = LineFillColor({"highway", "secondary"}, scale);
      TEST(secondary, (mapStyle, scale));
      uint32_t const bg = rules.GetBgColor(scale) & 0xFFFFFF;
      TEST_GREATER_OR_EQUAL(Contrast(*secondary, bg), 1.3, (mapStyle, scale));
    }
    auto const secondary = LineFillColor({"highway", "secondary"}, 15);
    auto const residential = LineFillColor({"highway", "residential"}, 15);
    TEST(residential, (mapStyle));
    TEST_GREATER_OR_EQUAL(Contrast(*secondary, *residential), 1.25, (mapStyle));
  });
}

// Rivers were among the most visible lines on the old dark map; keep them visible at night.
UNIT_TEST(Arah_DarkRiversVisible)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    if (!MapStyleIsDark(mapStyle))
      return;
    auto const river = LineFillColor({"waterway", "river"}, 13);
    TEST(river, (mapStyle));
    uint32_t const bg = drule::rules().GetBgColor(13) & 0xFFFFFF;
    TEST_GREATER_OR_EQUAL(Contrast(*river, bg), 2.5, (mapStyle));
  });
}

// Night driving needs a readable road hierarchy: trunk, primary and secondary must not merge into one color.
UNIT_TEST(Arah_DarkRoadHierarchy)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    if (!IsArahNightStyle(mapStyle))
      return;
    int constexpr kScale = 15;
    auto const trunk = LineFillColor({"highway", "trunk"}, kScale);
    auto const primary = LineFillColor({"highway", "primary"}, kScale);
    auto const secondary = LineFillColor({"highway", "secondary"}, kScale);
    TEST(trunk, ("No highway-trunk line rule", mapStyle, kScale));
    TEST(primary, ("No highway-primary line rule", mapStyle, kScale));
    TEST(secondary, ("No highway-secondary line rule", mapStyle, kScale));
    LOG(LINFO, (mapStyle, "trunk/primary", Contrast(*trunk, *primary), "primary/secondary",
                Contrast(*primary, *secondary), "trunk/secondary hue", HueDistance(*trunk, *secondary)));
    TEST_GREATER_OR_EQUAL(Contrast(*trunk, *primary), 1.2, (mapStyle));
    TEST_GREATER_OR_EQUAL(Contrast(*primary, *secondary), 1.2, (mapStyle));
    TEST_GREATER_OR_EQUAL(HueDistance(*trunk, *secondary), 10.0, (mapStyle));
  });
}

UNIT_TEST(Arah_DarkParksAndBuildingsVisible)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    if (!IsArahNightStyle(mapStyle))
      return;
    int constexpr kScale = 15;
    uint32_t const bg = drule::rules().GetBgColor(kScale) & 0xFFFFFF;
    auto const park = AreaFillColor({"leisure", "park"}, kScale);
    auto const building = AreaFillColor({"building"}, kScale);
    TEST(park, ("No leisure-park area rule", mapStyle, kScale));
    TEST(building, ("No building area rule", mapStyle, kScale));
    LOG(LINFO, (mapStyle, "park/bg", Contrast(*park, bg), "building/bg", Contrast(*building, bg)));
    TEST_GREATER_OR_EQUAL(Contrast(*park, bg), 1.25, (mapStyle));
    TEST_GREATER_OR_EQUAL(Contrast(*building, bg), 1.3, (mapStyle));
  });
}

UNIT_TEST(Arah_DarkParkLabelsReadable)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    if (!IsArahNightStyle(mapStyle))
      return;
    int constexpr kScale = 15;
    auto const park = AreaFillColor({"leisure", "park"}, kScale);
    auto const caption = AreaCaptionColor({"leisure", "park"}, kScale);
    TEST(park, ("No leisure-park area rule", mapStyle, kScale));
    TEST(caption, ("No leisure-park caption rule", mapStyle, kScale));
    uint32_t const text = BlendOver(*caption, *park);
    LOG(LINFO, (mapStyle, "park label/park", Contrast(text, *park)));
    TEST_GREATER_OR_EQUAL(Contrast(text, *park), 3.0, (mapStyle));
  });
}

// Street names must stay readable on the lighter Tenang night background, in every dark map mode.
UNIT_TEST(Arah_DarkRoadNamesReadable)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    if (!MapStyleIsDark(mapStyle))
      return;
    // Secondary road names use the light, medium and dark label greys at these scales.
    for (auto const & [scale, minContrast] : {std::pair{12, 3.5}, std::pair{15, 4.5}, std::pair{17, 4.5}})
    {
      auto const text = LineTextColor({"highway", "secondary"}, scale);
      TEST(text, ("No highway-secondary name rule", mapStyle, scale));
      uint32_t const bg = drule::rules().GetBgColor(scale) & 0xFFFFFF;
      double const contrast = Contrast(BlendOver(*text, bg), bg);
      LOG(LINFO, (mapStyle, scale, "secondary name/bg", contrast));
      TEST_GREATER_OR_EQUAL(contrast, minContrast, (mapStyle, scale));
    }
  });
}

// Vehicle palettes define @water_label twice (CoMaps' extra label block); the last one wins in kothic.
UNIT_TEST(Arah_VehicleWaterLabels)
{
  styles::RunForEveryMapStyle([](MapStyle mapStyle)
  {
    if (mapStyle != MapStyleVehicleLight && mapStyle != MapStyleVehicleDark)
      return;
    auto const text = LineTextColor({"waterway", "river"}, 15);
    TEST(text, (mapStyle));
    TEST_EQUAL(*text & 0xFFFFFF, mapStyle == MapStyleVehicleDark ? 0x7FB3D5u : 0x3F7FAFu, (mapStyle));
  });
}

// Pins Tenang accents and base colors beyond the route, so a mis-resolved upstream merge can't revert them.
UNIT_TEST(Arah_TenangAnchors)
{
  struct Named
  {
    std::string_view m_name;
    uint32_t m_light;
    uint32_t m_dark;
  };
  std::array<Named, 7> constexpr kDrape = {{
      {"Selection", 0x0F8B7E, 0x3DCFB6},
      {"RouteOutline", 0x0B6F65, 0x0F8B7E},
      {"Arrow3D", 0x14A593, 0x3DCFB6},
      {"DefaultTrackColor", 0x0F8B7E, 0x3DCFB6},
      {"SearchmarkDefault", 0x0F8B7E, 0x3DCFB6},
      {"RatingNone", 0x0F8B7E, 0x3DCFB6},
      {"TrafficOutline", 0xF4F1EA, 0x1B2023},
  }};
  styles::RunForEveryMapStyle([&](MapStyle mapStyle)
  {
    auto const & rules = drule::rules();
    bool const isDark = MapStyleIsDark(mapStyle);
    for (auto const & d : kDrape)
      TEST_EQUAL(rules.GetColor(std::string(d.m_name)) & 0xFFFFFF, isDark ? d.m_dark : d.m_light, (mapStyle, d.m_name));

    if (mapStyle != MapStyleDefaultLight && mapStyle != MapStyleDefaultDark)
      return;
    int constexpr kScale = 15;
    TEST_EQUAL(AreaFillColor({"natural", "water"}, kScale), isDark ? 0x1E3442u : 0xBCDCF3u, (mapStyle));
    TEST_EQUAL(LineFillColor({"waterway", "river"}, kScale), isDark ? 0x3E86AEu : 0x8EC3E8u, (mapStyle));
    TEST_EQUAL(LineFillColor({"highway", "residential"}, kScale), isDark ? 0x353B3Fu : 0xFDFDFCu, (mapStyle));
    TEST_EQUAL(LineFillColor({"highway", "secondary"}, kScale), isDark ? 0x5B5542u : 0xFDC862u, (mapStyle));
  });
}
}  // namespace arah_palette_test

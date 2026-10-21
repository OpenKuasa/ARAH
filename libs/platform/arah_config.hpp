#pragma once

#include <string_view>

// Arah-specific values, kept in one place so upstream CoMaps code stays easy to merge.
// Lines marked ARAH-PLACEHOLDER must get the owner's real value before release
// (tools/python/arah_brand_check.py --release fails while any remain).
namespace arah
{
inline constexpr std::string_view kAppName = "Arah";
// ARAH-PLACEHOLDER: Arah website
inline constexpr std::string_view kWebsiteUrl = "https://github.com/ARAH-ORG/arah";
// ARAH-PLACEHOLDER: Arah support email
inline constexpr std::string_view kSupportEmail = "support@arah.invalid";
// ARAH-PLACEHOLDER: Arah privacy policy
inline constexpr std::string_view kPrivacyUrl = "https://github.com/ARAH-ORG/arah/blob/main/PRIVACY.md";
// ARAH-PLACEHOLDER: Arah terms of use
inline constexpr std::string_view kTermsUrl = "https://github.com/ARAH-ORG/arah/blob/main/TERMS.md";
// Empty until Arah has a domain for share links: places are shared as OpenStreetMap links.
inline constexpr std::string_view kShareLinkBase = "";
// CoMaps' metaserver may hand out a donate link; Arah doesn't show CoMaps donations.
inline constexpr bool kAcceptMetaserverDonateUrl = false;
// ARAH-PLACEHOLDER: iOS bundle ids my.arah.app(.debug/.tests/.widgetextension) in project.pbxproj
// ARAH-PLACEHOLDER: iCloud containers iCloud.my.arah.app(.debug) in iphone/Maps/CoMaps-*.entitlements
}  // namespace arah

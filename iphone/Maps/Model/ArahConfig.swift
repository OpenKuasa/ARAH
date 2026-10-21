import Foundation

/// Arah-specific values for the iPhone app, mirroring libs/platform/arah_config.hpp.
/// An empty (nil) URL hides the screen row that would open it.
enum ArahConfig {
  static let appName = "Arah"
  // ARAH-PLACEHOLDER: Arah website
  static let websiteURL = URL(string: "https://github.com/ARAH-ORG/arah")!
  // ARAH-PLACEHOLDER: Arah privacy policy
  static let privacyURL = URL(string: "https://github.com/ARAH-ORG/arah/blob/main/PRIVACY.md")!
  // ARAH-PLACEHOLDER: Arah terms of use
  static let termsURL = URL(string: "https://github.com/ARAH-ORG/arah/blob/main/TERMS.md")!
  // ARAH-PLACEHOLDER: Arah support email
  static let supportEmail = "support@arah.invalid"
  static let appStoreReviewURL: URL? = nil
  static let newsURL: URL? = nil
  static let volunteerURL: URL? = nil
  static let socialMediaEnabled = false
}

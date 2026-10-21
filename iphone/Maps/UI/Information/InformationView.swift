import SwiftUI

/// View for the about information
struct InformationView: View {
    // MARK: Properties
    
    /// The dismiss action of the environment
    @Environment(\.dismiss) private var dismiss
    
    
    /// The open url action of the environment
    @Environment(\.openURL) private var openUrl
    
    
    /// If the FAQ should be shown in the Safari view
    @State var showFaq: Bool = false
    
    
    /// If the privacy policy should be shown in the Safari view
    @State private var showPrivacyPolicy: Bool = false
    
    
    /// If the therms of use  should be shown in the Safari view
    @State private var showTermsOfUse: Bool = false
    
    
    /// The app name
    private var appName: String? {
        return Bundle.main.object(forInfoDictionaryKey: "CFBundleDisplayName") as? String
    }
    
    
    /// The app version
    private var appVersion: String? {
        return Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String
    }
    
    
    /// The app build number
    private var appBuild: String? {
        return Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String
    }
    
    
    /// The information to copy when long pressing the version number
    private var copyInformation: String? {
        if let appVersion, let appBuild {
            let dateFormatter = DateFormatter()
            dateFormatter.locale = Locale(identifier: "en_US_POSIX")
            dateFormatter.dateFormat = "yyMMdd"
            if let date = dateFormatter.date(from: String(FrameworkHelper.dataVersion())) {
                dateFormatter.dateFormat = "yyyy-MM-dd"
                return String(localized: "version: \(appVersion) (\(appBuild))\nmap data: \(dateFormatter.string(from: date))")
            }
        }
        
        return nil
    }
    
    
    /// The actual view
    var body: some View {
        NavigationView {
            List {
                Section {
                    if #available(iOS 16, *) {
                        AboutCoMapsView()
                        .alignmentGuide(.listRowSeparatorLeading) { _ in
                            return 0
                        }
                    } else {
                        AboutCoMapsView()
                    }
                    
                    NavigationLink(isActive: $showFaq) {
                        FaqView()
                    } label: {
                        Label("faq", systemImage: "questionmark.circle")
                            .foregroundStyle(.alternativeAccent)
                    }
                    .tint(.alternativeAccent)
                    
                    Button {
                        MailComposer.sendBugReportWith(title: "Bug Report")
                    } label: {
                        Label("report_a_bug", systemImage: "exclamationmark.bubble")
                    }
                    .tint(.alternativeAccent)
                    
                    if let newsURL = ArahConfig.newsURL {
                        Button {
                            openUrl(newsURL)
                        } label: {
                            Label("news", systemImage: "newspaper")
                        }
                        .tint(.alternativeAccent)
                    }
                    
                    if let volunteerURL = ArahConfig.volunteerURL {
                        Button {
                            openUrl(volunteerURL)
                        } label: {
                            Label("volunteer", systemImage: "person.wave.2")
                        }
                        .tint(.alternativeAccent)
                    }
                    
                    if let appStoreReviewURL = ArahConfig.appStoreReviewURL {
                        Button {
                            openUrl(appStoreReviewURL)
                        } label: {
                            Label("rate_the_app", systemImage: "star")
                        }
                        .tint(.alternativeAccent)
                    }
                }
                
                Section {
                    if #available(iOS 16, *) {
                        ApoutOpenStreetMapView()
                        .alignmentGuide(.listRowSeparatorLeading) { _ in
                            return 0
                        }
                    } else {
                        ApoutOpenStreetMapView()
                    }
                    
                    Button {
                        openUrl(URL(string: "https://www.openstreetmap.org/fixthemap")!)
                    } label: {
                        if #available(iOS 17.0, *) {
                            Label("report_incorrect_map_bug", systemImage: "exclamationmark.magnifyingglass")
                        } else {
                            Label("report_incorrect_map_bug", systemImage: "exclamationmark.bubble")
                        }
                    }
                    .tint(.alternativeAccent)
                }
                
                Section {
                    ForEach(ArahConfig.socialMediaEnabled ? SocialMedia.allCases : []) { socialMedia in
                        Button {
                            openUrl(socialMedia.url)
                        } label: {
                            Label {
                                Text(socialMedia.description)
                            } icon: {
                                socialMedia.image
                                    .resizable()
                                    .aspectRatio(contentMode: .fit)
                            }
                        }
                        .tint(.alternativeAccent)
                    }
                } header: {
                    if ArahConfig.socialMediaEnabled {
                        Text("follow_us")
                    }
                } footer: {
                    VStack(spacing: 8) {
                        Button {
                            showPrivacyPolicy = true
                        } label: {
                            Text("privacy_policy")
                        }
                        .sheet(isPresented: $showPrivacyPolicy) {
                            SafariView(url: ArahConfig.privacyURL, dismissButton: .close)
                        }
                        
                        Button {
                            showTermsOfUse = true
                        } label: {
                            Text("terms_of_use")
                        }
                        .sheet(isPresented: $showTermsOfUse) {
                            SafariView(url: ArahConfig.termsURL, dismissButton: .close)
                        }
                        
                        NavigationLink {
                            CopyrightView()
                        } label: {
                            Text("copyright")
                        }
                        
                        Text("about_based_on")
                    }
                    .tint(.secondary)
                    .padding(.top)
                    .frame(maxWidth: .infinity)
                }
            }
            .accentColor(.accent)
            .navigationTitle(appName ?? String())
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Menu {
                        Button {
                            if let copyInformation {
                                UIPasteboard.general.string = copyInformation
                            }
                        } label: {
                            Label("copy_to_clipboard", systemImage: "document.on.clipboard")
                        }
                    } label: {
                        VStack {
                            if let appName {
                                Text(appName)
                                    .font(.title3)
                                    .bold()
                                    .foregroundStyle(.white)
                                    .foregroundStyle(.white.opacity(0.96))
                            }
                            
                            if let appVersion, let appBuild {
                                Text("version \(appVersion) (\(appBuild))")
                                    .font(.caption2)
                                    .foregroundStyle(.white.opacity(0.92))
                            }
                        }
                    }
                }
                
                ToolbarItem(placement: .confirmationAction) {
                    if #available(iOS 26, *) {
                        Button {
                            dismiss()
                        } label: {
                            Label("close", systemImage: "xmark")
                        }
                        .buttonStyle(.glassProminent)
                    } else {
                        Button {
                            dismiss()
                        } label: {
                            Text("close")
                        }
                    }
                }
            }
        }
        .navigationViewStyle(StackNavigationViewStyle())
        .accentColor(.toolbarAccent)
    }
}

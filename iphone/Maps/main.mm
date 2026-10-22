#import "MapsAppDelegate.h"
#import "MWMSettings.h"

#include "platform/platform.hpp"

// Arah opens in Malay on first launch. Later launches keep whatever language the user picks in iOS Settings.
static void ApplyArahDefaultLanguage()
{
  NSString * const kAppliedKey = @"ArahDefaultLanguageApplied";
  NSUserDefaults * defaults = NSUserDefaults.standardUserDefaults;
  // Unit tests run inside the app and expect upstream's English.
  if ([defaults boolForKey:kAppliedKey] || NSProcessInfo.processInfo.environment[@"XCTestConfigurationFilePath"])
    return;
  [defaults setObject:@[@"ms"] forKey:@"AppleLanguages"];
  [defaults setBool:YES forKey:kAppliedKey];
}

int main(int argc, char * argv[])
{
  ApplyArahDefaultLanguage();
  [MWMSettings initializeLogging];

  NSBundle * mainBundle = [NSBundle mainBundle];
  NSString * appName = [mainBundle objectForInfoDictionaryKey:@"CFBundleName"];
  NSString * bundleId = mainBundle.bundleIdentifier;
  auto & p = GetPlatform();
  LOG(LINFO, (appName.UTF8String, bundleId.UTF8String, p.Version(), "started, detected CPU cores:", p.CpuCores()));

  int retVal;
  @autoreleasepool
  {
    retVal = UIApplicationMain(argc, argv, nil, NSStringFromClass([MapsAppDelegate class]));
  }
  return retVal;
}

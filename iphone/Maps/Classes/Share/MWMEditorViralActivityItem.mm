#import "MWMEditorViralActivityItem.h"

#include "platform/arah_config.hpp"

#include <string>

@implementation MWMEditorViralActivityItem

#pragma mark - UIActivityItemSource

- (id)activityViewControllerPlaceholderItem:(UIActivityViewController *)activityViewController
{
  return @"";
}

- (id)activityViewController:(UIActivityViewController *)activityViewController
         itemForActivityType:(NSString *)activityType
{
  if ([activityType isEqualToString:UIActivityTypePostToFacebook] ||
      [activityType isEqualToString:@"com.facebook.Facebook.ShareExtension"] ||
      [activityType.lowercaseString rangeOfString:@"facebook"].length)
  {
    return [NSURL URLWithString:@(std::string(arah::kWebsiteUrl).c_str())];
  }

  NSString * websiteURL = @(std::string(arah::kWebsiteUrl).c_str());
  if ([activityType isEqualToString:UIActivityTypePostToTwitter] || [activityType isEqualToString:UIActivityTypeMail])
    return [NSString stringWithFormat:@"%@ %@", L(@"whatsnew_editor_message_1"), websiteURL];

  return [NSString stringWithFormat:@"%@.\n%@\n%@", L(@"editor_sharing_title"), L(@"whatsnew_editor_message_1"), websiteURL];
}

- (NSString *)activityViewController:(UIActivityViewController *)activityViewController
              subjectForActivityType:(NSString *)activityType
{
  return L(@"editor_sharing_title");
}

@end

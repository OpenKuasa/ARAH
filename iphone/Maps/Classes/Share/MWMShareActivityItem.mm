#import "MWMShareActivityItem.h"

#include <CoreApi/Framework.h>
#import <CoreApi/PlacePageData.h>
#import <CoreApi/PlacePagePreviewData.h>
#import <CoreApi/PlacePageInfoData.h>
#import <CoreApi/PlacePagePhone.h>
#import <LinkPresentation/LPLinkMetadata.h>

#include "map/arah_share.hpp"
#include "platform/arah_config.hpp"

NSString * httpGe0Url(NSString * shortUrl)
{
  // Replace the 'comaps://' scheme with Arah's share-link domain (only used once Arah has one).
  return [shortUrl stringByReplacingCharactersInRange:NSMakeRange(0, 9)
                                           withString:@(std::string(arah::kShareLinkBase).c_str())];
}

@interface MWMShareActivityItem ()

@property(nonatomic) PlacePageData *data;
@property(nonatomic) CLLocationCoordinate2D location;
@property(nonatomic) BOOL isMyPosition;

@end

@implementation MWMShareActivityItem

- (instancetype)initForMyPositionAtLocation:(CLLocationCoordinate2D const &)location
{
  self = [super init];
  if (self)
  {
    _location = location;
    _isMyPosition = YES;
  }
  return self;
}

- (instancetype)initForPlacePageObject:(id<MWMPlacePageObject>)object
{
  NSAssert(false, @"deprecated");

  return nil;
}

- (instancetype)initForPlacePage:(PlacePageData *)data {
  self = [super init];
  if (self)
  {
    NSAssert(data, @"Entity can't be nil!");
    _isMyPosition = data.isMyPosition;
    _data = data;
  }
  return self;
}

- (NSString *)url:(BOOL)isShort
{
  auto & f = GetFramework();

  auto const title = ^NSString *(PlacePageData *data)
  {
    if (!data || data.isMyPosition)
      return L(@"core_my_position");
    else if (data.previewData.title.length > 0)
      return data.previewData.title;
    else if (data.previewData.subtitle.length)
      return data.previewData.subtitle;
    else if (data.previewData.secondarySubtitle.length)
      return data.previewData.secondarySubtitle;
    else
      return @"";
  };

  ms::LatLon const ll = self.data ? ms::LatLon(self.data.locationCoordinate.latitude,
                                               self.data.locationCoordinate.longitude)
                                    : ms::LatLon(self.location.latitude, self.location.longitude);
  std::string const & s = f.CodeGe0url(ll.m_lat, ll.m_lon, f.GetDrawScale(), title(self.data).UTF8String);

  NSString * url = @(s.c_str());
  if (!isShort)
    return url;
  NSUInteger const kGe0UrlLength = 16;
  return [url substringWithRange:NSMakeRange(0, kGe0UrlLength)];
}

- (ms::LatLon)latLon
{
  return self.data ? ms::LatLon(self.data.locationCoordinate.latitude, self.data.locationCoordinate.longitude)
                   : ms::LatLon(self.location.latitude, self.location.longitude);
}

// Arah has no share-link domain yet, so places are shared as OpenStreetMap links.
- (NSString *)shareLink
{
  if (!arah::kShareLinkBase.empty())
    return httpGe0Url([self url:NO]);
  ms::LatLon const ll = [self latLon];
  return @(arah::ShareLink(ll.m_lat, ll.m_lon, GetFramework().GetDrawScale()).c_str());
}

#pragma mark - UIActivityItemSource

- (id)activityViewControllerPlaceholderItem:(UIActivityViewController *)activityViewController
{
  return [self url:YES];
}

- (id)activityViewController:(UIActivityViewController *)activityViewController
         itemForActivityType:(NSString *)activityType
{
  NSString * type = activityType;
  if ([UIActivityTypePostToTwitter isEqualToString:type])
    return self.itemForTwitter;
  return [self itemDefaultWithActivityType:type];
}

- (NSString *)activityViewController:(UIActivityViewController *)activityViewController
              subjectForActivityType:(NSString *)activityType
{
  return [self subjectDefault];
}

- (LPLinkMetadata *)activityViewControllerLinkMetadata:(UIActivityViewController *)activityViewController API_AVAILABLE(ios(13.0))
{
  LPLinkMetadata * metadata = [[LPLinkMetadata alloc] init];
  metadata.originalURL = [NSURL URLWithString:[self shareLink]];
  metadata.title = self.isMyPosition ? L(@"core_my_position") : self.data.previewData.title;
  metadata.iconProvider = [[NSItemProvider alloc] initWithObject:[UIImage imageNamed:@"Logo"]];
  return metadata;
}

#pragma mark - Message

- (NSString *)itemForTwitter
{
  return [NSString stringWithFormat:@"%@\n%@", [self shareLink],
                                    self.isMyPosition ? L(@"my_position_share_email_subject")
                                                      : self.data.previewData.title];
}

- (NSString *)itemDefaultWithActivityType:(NSString *)activityType
{
  NSString * url = [self shareLink];
  if (self.isMyPosition)
  {
    BOOL const hasSubject = [activityType isEqualToString:UIActivityTypeMail];
    if (hasSubject)
      return url;
    return [NSString
        stringWithFormat:@"%@ %@", L(@"my_position_share_email_subject"), url];
  }

  NSMutableArray *phones = [NSMutableArray new];
  [self.data.infoData.phones enumerateObjectsUsingBlock:^(PlacePagePhone * _Nonnull phone, NSUInteger idx, BOOL * _Nonnull stop) {
    [phones addObject:phone.phone];
  }];

  NSMutableArray<NSString *> * details = [NSMutableArray new];
  for (NSString * str in @[self.data.previewData.subtitle ?: @"", self.data.previewData.secondarySubtitle ?: @"",
                           [phones componentsJoinedByString:@"; "]])
  {
    if (str.length)
      [details addObject:str];
  }

  ms::LatLon const ll = [self latLon];
  std::string const text = arah::ShareText((self.data.previewData.title ?: @"").UTF8String,
                                           [details componentsJoinedByString:@"\n"].UTF8String, ll.m_lat, ll.m_lon,
                                           GetFramework().GetDrawScale());
  return [NSString stringWithFormat:@"%@\n%@", L(@"sharing_call_action_look"), @(text.c_str())];
}

#pragma mark - Subject

- (NSString *)subjectDefault
{
  return self.isMyPosition ? L(@"my_position_share_email_subject")
                           : L(@"bookmark_share_email_subject");
}

@end

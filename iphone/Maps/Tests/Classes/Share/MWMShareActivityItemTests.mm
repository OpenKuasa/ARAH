#import <XCTest/XCTest.h>
#import "MWMShareActivityItem.h"

#include "ge0/url_generator.hpp"
#include "platform/arah_config.hpp"

#include <string>

extern NSString * httpGe0Url(NSString * shortUrl);

#pragma mark - Unit

@interface MWMShareActivityItemTests : XCTestCase
@end

@implementation MWMShareActivityItemTests

// Arah: the ge0 link uses Arah's share domain (empty until Arah has one; places are then shared as OSM links).
static NSString * ArahShareBase() { return @(std::string(arah::kShareLinkBase).c_str()); }

- (void)testHttpGe0UrlReplacesPrefix {
    XCTAssertEqualObjects(httpGe0Url(@"comaps://o4CoCoCoCo/Test_Location"),
                          [ArahShareBase() stringByAppendingString:@"o4CoCoCoCo/Test_Location"]);
}

@end

#pragma mark - Integration

@interface ShareUrlIntegrationTests : XCTestCase
@end

@implementation ShareUrlIntegrationTests

- (void)testGenerateShortShowMapUrlUsesCoMapsPrefix {
    std::string const url = ge0::GenerateShortShowMapUrl(50.0, 0.0, 14.0, "Test Location");
    
    NSString * const shortUrl = @(url.c_str());
    
    XCTAssertTrue([shortUrl hasPrefix:@"comaps://"], @"Expected 'comaps://' prefix, got: %@", shortUrl);
}

- (void)testStringIsFormattedCorrectly {
    std::string const url = ge0::GenerateShortShowMapUrl(50.0, 0.0, 14.0, "Test Location");
    
    NSString * const httpUrl = httpGe0Url(@(url.c_str()));
    
    XCTAssertEqualObjects(httpUrl, [@(std::string(arah::kShareLinkBase).c_str()) stringByAppendingString:@"o4CoCoCoCo/Test_Location"]);
}

@end

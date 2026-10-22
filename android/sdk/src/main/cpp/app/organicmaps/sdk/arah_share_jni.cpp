#include "app/organicmaps/sdk/Framework.hpp"
#include "app/organicmaps/sdk/core/jni_helper.hpp"

#include "map/arah_share.hpp"

namespace
{
// Same rule as nativeGetGe0Url: a zoom level of 0 or less means the current map scale.
int ShareZoom(jdouble zoomLevel)
{
  return static_cast<int>(zoomLevel > 0 ? zoomLevel : frm()->GetDrawScale());
}
}  // namespace

extern "C"
{
JNIEXPORT jstring JNICALL Java_app_organicmaps_sdk_util_ArahShare_nativeShareLink(JNIEnv * env, jclass, jdouble lat,
                                                                                  jdouble lon, jdouble zoomLevel)
{
  return jni::ToJavaString(env, arah::ShareLink(lat, lon, ShareZoom(zoomLevel)));
}

JNIEXPORT jstring JNICALL Java_app_organicmaps_sdk_util_ArahShare_nativeShareText(JNIEnv * env, jclass, jstring name,
                                                                                  jstring details, jdouble lat,
                                                                                  jdouble lon, jdouble zoomLevel)
{
  return jni::ToJavaString(env, arah::ShareText(jni::ToNativeString(env, name), jni::ToNativeString(env, details), lat,
                                                lon, ShareZoom(zoomLevel)));
}
}  // extern "C"
